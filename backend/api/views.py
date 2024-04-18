from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.serializers import (
    TagModelSerializer,
    IngredientModelSerializer,
    RecipeReadModelSerializer,
    RecipeWriteModelSerializer,
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
            # queryset = queryset.prefetch_related('follow_set__to_user')
            # queryset = queryset.prefetch_related('follow_set__from_user')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return settings.SERIALIZERS.user
        return super().get_serializer_class()


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
        return RecipeWriteModelSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
