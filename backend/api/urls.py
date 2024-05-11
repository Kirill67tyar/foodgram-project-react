from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientReadOnlyModelViewSet, RecipeModelViewSet,
                       TagReadOnlyModelViewSet, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagReadOnlyModelViewSet, basename='tags')
router.register('ingredients', IngredientReadOnlyModelViewSet,
                basename='ingredients')
router.register('recipes', RecipeModelViewSet, basename='recipes')
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
