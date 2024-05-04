from django_filters.rest_framework import DjangoFilterBackend
from io import BytesIO
from rest_framework.filters import SearchFilter
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import render
from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.views import UserViewSet as DjoserUserViewSet

import rest_framework.serializers
from rest_framework.serializers import (
    ValidationError,
)
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.permissions import (
    IsAuthenticatedAndAuthorOrReadOnly,
)
from api.filters import (
    IngredientFilter,
    RecipeFilter,
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
    # permission_classes = (IsAuthenticated,)  # ! как временный вариант
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    # pagination_class = PageNumberPagination

    # def get_object(self):
    #     if self.action == 'subscribe':
    #         queryset = self.filter_queryset(self.get_queryset())
    #         lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
    #         assert lookup_url_kwarg in self.kwargs, (
    #             'Expected view %s to be called with a URL keyword argument '
    #             'named "%s". Fix your URL conf, or set the `.lookup_field` '
    #             'attribute on the view correctly.' %
    #             (self.__class__.__name__, lookup_url_kwarg)
    #         )
    #         filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
    #         user = queryset.filter(**filter_kwargs).first()
    #         if not user:
    #             raise ValidationError('asdasd')
    #     return super().get_object()


    def get_permissions(self):
        if self.action == 'me':
            # self.permission_classes = [
            #     IsAuthenticated,
            # ],
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

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
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscriptions(self, request):
        return self.list(request)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[
            IsAuthenticated,
        ],
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
                if user_to_follow == user:
                    raise ValidationError(
                        'error_msg'
                    )
                user.following.add(user_to_follow)
                serializer = self.get_serializer(
                    user_to_follow
                )
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED)
            raise ValidationError(
                'error_msg'
            )
        else:
            if user_in_following:
                user.following.remove(user_to_follow)
                return Response(
                    status=status.HTTP_204_NO_CONTENT)
            # raise ValidationError(
            #     'error_msg'
            # )
        return Response(
            # data=data,
            status=status.HTTP_400_BAD_REQUEST,
            # status=status.HTTP_409_CONFLICT
        )


class TagReadOnlyModelViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagModelSerializer
    pagination_class = None


class IngredientReadOnlyModelViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientModelSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    filterset_fields = ('name',)


class RecipeModelViewSet(ModelViewSet):
    permission_classes = (IsAuthenticatedAndAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = (
        'author',
        'tags',
    )

    queryset = Recipe.objects.select_related(
        'author',
    ).prefetch_related(
        'tags',
        'ingredients',
        'recipeingredient_set__ingredient',
        'author__following',
    )
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]

    def get_queryset(self):
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        is_favorited = self.request.query_params.get(
            'is_favorited')
        if is_in_shopping_cart is not None and bool(is_in_shopping_cart) == 1:
            user = self.request.user
            if user.is_authenticated:
                order = user.orders.filter(downloaded=False).first()
                if order:
                    return self.queryset.filter(orders__order=order)
        if is_favorited is not None and bool(is_favorited) == 1:
            user = self.request.user
            if user.is_authenticated:
                return user.favorites.all()
        return self.queryset

    def get_object(self):
        if self.action in ('shopping_cart', 'favorite',) and self.request.method == 'POST':
            queryset = self.filter_queryset(self.get_queryset())
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
            )
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            recipe = queryset.filter(**filter_kwargs).first()
            if not recipe:
                raise ValidationError('asdasd')
            # if not recipe and self.request.method == 'DELETE':
            #     # raise ValidationError(code=404)
            #     try:
            #         raise ValidationError('asdasd')        
            #     except ValidationError as exc:
            #         exc.status_code = 404
            #         raise exc
            # raise ValidationError('asdasd')
        return super().get_object()

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
        permission_classes=[
            IsAuthenticated,
        ],
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
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def shopping_cart(self, request, pk):  #
        user = request.user
        recipe = self.get_object()
        order = user.orders.filter(downloaded=False).first()
        if not order:
            order = user.orders.create()
        # if not recipe:
        #     raise ValidationError('asdasd')
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
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        methods=['get',],
        url_path='download_shopping_cart',
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def download_shopping_cart(self, request):
        user = request.user
        order = user.orders.filter(downloaded=False).first()
        if not order:
            # return HttpResponse(status=200)
            return HttpResponse(status=200)
        order.downloaded = True
        recipe_order_lst = order.items.select_related(
            'recipe'
        ).prefetch_related(
            'recipe__recipeingredient_set__ingredient'
        )
        data = {}
        for r_o in recipe_order_lst:
            for i in r_o.recipe.recipeingredient_set.all():
                key = (i.ingredient.name, i.ingredient.measurement_unit,)
                data[key] = data.get(key, 0) + i.amount
        # content = loader.render_to_string(
        #     template_name='orders/order_template.html',
        #     context={
        #         # 'order': order,
        #     },
        #     request=request
        # )
        # ? ----- формирование файла --------
        content = 'тааа-шааа'
        # ? ----- формирование файла --------
        buffer = BytesIO()
        buffer.write(bytes(content, encoding='utf-8'))
        buffer.seek(0)
        a = 12345
        response = HttpResponse(
            buffer, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="file-{a}.txt"'
        # response['Content-Disposition'] = f'attachment; filename="file-{a}.html"'

        return response


# http://127.0.0.1:8000/api/recipes-temprorary/download_shopping_cart/
@permission_classes([IsAuthenticated,])
@api_view(http_method_names=['GET'])
def download_cart_view(request):
    user = request.user
    order = user.orders.filter(downloaded=False).first()
    if not order:
        # return HttpResponse(status=200)
        return HttpResponse(status=200)
    order.downloaded = True
    recipe_order_lst = order.items.select_related(
        'recipe'
    ).prefetch_related(
        'recipe__recipeingredient_set__ingredient'
    )
    data = {}
    for r_o in recipe_order_lst:
        for i in r_o.recipe.recipeingredient_set.all():
            key = (i.ingredient.name, i.ingredient.measurement_unit,)
            data[key] = data.get(key, 0) + i.amount
    # content = loader.render_to_string(
    #     template_name='orders/order_template.html',
    #     context={
    #         # 'order': order,
    #     },
    #     request=request
    # )
    # ? ----- формирование файла --------
    content = 'тааа-шааа'
    # ? ----- формирование файла --------
    buffer = BytesIO()
    buffer.write(bytes(content, encoding='utf-8'))
    buffer.seek(0)
    a = 12345
    response = HttpResponse(buffer, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="file-{a}.txt"'
    # response['Content-Disposition'] = f'attachment; filename="file-{a}.html"'

    return response


"""
rss = order.items.prefetch_related('recipe__recipeingredient_set__ingredient')
или даже так (3 sql запроса а не 4):
rsss = order.items.select_related('recipe').prefetch_related('recipe__recipeingredient_set__ingredient')

In [41]: for r in rss:
    ...:     for i in r.recipe.recipeingredient_set.all():
    ...:         print(i.ingredient.name, i.amount)
"""
