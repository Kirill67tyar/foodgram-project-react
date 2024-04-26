from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import render
from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.views import UserViewSet as DjoserUserViewSet

import rest_framework.serializers
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.serializers import (
    TagModelSerializer,
    IngredientModelSerializer,
    RecipeReadModelSerializer,
    RecipeWriteModelSerializer,
    RecipeToFavoriteModelSerializer,
    UserSubscriptionsModelSerializer,
)
from orders.models import (
    Order,
    RecipeOrder,
)
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
)
from users.models import Follow


"""
По переопределению обработчиков для djoser может быть полезна:
https://stackoverflow.com/questions/71735934/djoser-override-perform-create-method-of-class-userviewset
https://stackoverflow.com/questions/66036497/djoser-override-registration

"""

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    permission_classes = (IsAuthenticated,)  # ! как временный вариант

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # queryset = queryset.prefetch_related('followers')
            queryset = queryset.prefetch_related('following')
        elif self.action == 'subscriptions':
            user = self.request.user
            queryset = user.following.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return settings.SERIALIZERS.user
        if self.action in ('subscriptions', 'subscribe',):
            return UserSubscriptionsModelSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get',],
        url_path='subscriptions',
        # permission_classes=[
        #     IsAuthenticated,
        # ],
    )
    def subscriptions(self, request):
        return self.list(request)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        # permission_classes=[
        #     IsAuthenticated,
        # ],
    )
    def subscribe(self, request, id):
        """
        ! написать проверку, чтобы пользователь не мог подписаться на самого себя
        """
        user = request.user
        user_to_follow = self.get_object()
        user_in_following = Follow.objects.filter(
            from_user=user,
            to_user=user_to_follow).exists()
        if request.method == 'POST':
            if not user_in_following:
                user.following.add(user_to_follow)
                serializer = self.get_serializer(
                    user_to_follow
                )
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED)
        else:
            if user_in_following:
                user.following.remove(user_to_follow)
                return Response(
                    status=status.HTTP_204_NO_CONTENT)
        return Response(
            # data=data,
            # status=status.HTTP_400_BAD_REQUEST,
            status=status.HTTP_409_CONFLICT
        )


class TagReadOnlyModelViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagModelSerializer
    pagination_class = None


class IngredientReadOnlyModelViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientModelSerializer
    pagination_class = None


class RecipeModelViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author',
    ).prefetch_related(
        'tags',
        'ingredients',
        'recipeingredient_set__ingredient',
        'author__following',
    )
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadModelSerializer
        elif self.action in ('favorite', 'shopping_cart', ):
            return RecipeToFavoriteModelSerializer
        return RecipeWriteModelSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        # permission_classes=[
        #     IsAuthenticated,
        # ],
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = self.get_object()
        if recipe:
            recipe_in_favorite = user.favorites.filter(
                favorite__recipe=recipe).exists()
            if request.method == 'POST':
                if not recipe_in_favorite:
                    user.favorites.add(recipe)
                    serializer = self.get_serializer(
                        # instance=recipe
                        recipe
                    )
                    return Response(
                        data=serializer.data,
                        status=status.HTTP_201_CREATED)
            else:
                if recipe_in_favorite:
                    user.favorites.remove(recipe)
                    return Response(
                        # data=data,
                        status=status.HTTP_204_NO_CONTENT)
        return Response(
            # data=data,
            # status=status.HTTP_400_BAD_REQUEST,
            status=status.HTTP_409_CONFLICT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        # permission_classes=[
        #     IsAuthenticated,
        # ],
    )
    def shopping_cart(self, request, pk):  # 
        user = request.user
        recipe = self.get_object()
        order = user.orders.filter(downloaded=False).first()
        if not order:
            order = user.orders.create()
        recipe_in_order_for_current_user = RecipeOrder.objects.filter(
            recipe=recipe,
            order=order,
        ).first()
        if request.method == 'POST':
            if not recipe_in_order_for_current_user:
                RecipeOrder.objects.create(
                    recipe=recipe,
                    order=order,
                )
                serializer = self.get_serializer(recipe)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        else:
            if recipe_in_order_for_current_user:
                recipe_in_order_for_current_user.delete()
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )
        return Response(
            # data=data,
            # status=status.HTTP_400_BAD_REQUEST,
            status=status.HTTP_409_CONFLICT
        )
from io import BytesIO



# http://127.0.0.1:8000/api/recipes-temprorary/download_shopping_cart/
@permission_classes([IsAuthenticated,])
# @permission_classes([AllowAny,])
@api_view(http_method_names=['GET'])
def download_cart_view(request):
    user = request.user
    order = user.orders.filter(downloaded=False).first()
    if not order:
        # return HttpResponse(status=200)
        return HttpResponse(status=status.HTTP_200_OK)
    order.items.all()
    data = {}  # ingredient: count
    content = 'тааа-шааа'
    buffer = BytesIO()
    buffer.write(bytes(content, encoding='utf-8'))
    buffer.seek(0)
    a = 12345
    response = HttpResponse(buffer, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="file-{a}.txt"'
    
    return response
    
"""
rss = order.items.prefetch_related('recipe__recipeingredient_set__ingredient')
или даже так (3 sql запроса а не 4):
rsss = order.items.select_related('recipe').prefetch_related('recipe__recipeingredient_set__ingredient')

In [41]: for r in rss:
    ...:     for i in r.recipe.recipeingredient_set.all():
    ...:         print(i.ingredient.name, i.amount)
"""


