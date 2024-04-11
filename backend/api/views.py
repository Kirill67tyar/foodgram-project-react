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
            queryset = queryset.prefetch_related('followers')
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
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadModelSerializer
