from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    # url(r'^', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]


