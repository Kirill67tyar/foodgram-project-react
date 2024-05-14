from django_filters.rest_framework import (CharFilter, FilterSet,
                                           ModelMultipleChoiceFilter, BooleanFilter,)
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
    is_in_shopping_cart = BooleanFilter(method='filter_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')

    def filter_shopping_cart(self, queryset, name, value):
        if bool(self.request.user.is_authenticated and value):
            order = self.request.user.orders.filter(downloaded=False).first()
            if order:
                return order.recipe.all()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if bool(self.request.user.is_authenticated and value):
            return queryset.filter(in_favorite__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
        ]
