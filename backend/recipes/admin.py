# from django.contrib import admin

# from recipes.models import Ingredient, Recipe, Tag


# class RecipeIngredientInline(admin.TabularInline):
#     model = Recipe.ingredients.through
#     extra = 1


# class RecipeTagInline(admin.TabularInline):
#     model = Recipe.tags.through
#     extra = 1


# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'author',)
#     list_filter = ('name', 'author',)

#     inlines = [RecipeIngredientInline, RecipeTagInline]

#     readonly_fields = ('in_favorites_count', )
#     # def get_fields(self, request, obj=None):
#     #     fields = super().get_fields(request, obj)
#     #     if obj:
#     #         fields += ('in_favorites_count',)
#     #     return fields

#     def in_favorites_count(self, obj):
#         return obj.in_favorites.count()

#     in_favorites_count.short_description = 'Count in favorite'


# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Ingredient)
# admin.site.register(Tag)
