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


class TagFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Tag
        fields = ['tags',]


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id', lookup_expr='icontains')
    # tags = CharFilter(field_name='tags__slug', lookup_expr='icontains')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        # field_name='tags',
        to_field_name='slug',
        # field_name='slug',
        # lookup_expr='slug__icontains',
        queryset=Tag.objects.all(),
    )
    # tags = MultipleChoiceFilter(
    #     field_name='tags__slug',
    #     #   lookup_expr='icontains'
    # )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
        ]
