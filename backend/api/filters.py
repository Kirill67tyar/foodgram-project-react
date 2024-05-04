from django_filters.rest_framework import (
    ModelMultipleChoiceFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
    MultipleChoiceFilter)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = [
            'name',
        ]




class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id', lookup_expr='icontains')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    # is_in_shopping_cart = ...
    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
            # 'is_in_shopping_cart',
        ]
