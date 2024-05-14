from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserModelAdmin(UserAdmin):
    list_display = ('pk', 'username',)
    list_filter = ('username', 'email', 'first_name',)
    search_fields = ('username', 'email', 'first_name',)


admin.site.register(Follow)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
