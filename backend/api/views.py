from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
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
)
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
)


"""
По переопределению обработчиков для djoser может быть полезна:
https://stackoverflow.com/questions/71735934/djoser-override-perform-create-method-of-class-userviewset
https://stackoverflow.com/questions/66036497/djoser-override-registration

"""

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
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
        elif self.action == 'favorite':
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
