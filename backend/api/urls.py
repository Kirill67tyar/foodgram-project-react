from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    TagReadOnlyModelViewSet,
    IngredientReadOnlyModelViewSet,
    RecipeModelViewSet,
    download_cart_view,
)


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagReadOnlyModelViewSet, basename='tags')
router.register('ingredients', IngredientReadOnlyModelViewSet,
                basename='ingredients')
router.register('recipes', RecipeModelViewSet, basename='recipes')
urlpatterns = [
    # path('recipes/download_shopping_cart/', download_cart_view, name='download'),
    path('', include(router.urls)),
    # url(r'^', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

