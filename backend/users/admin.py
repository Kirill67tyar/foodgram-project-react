from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class RecipeModelAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username',)
    list_filter = ('username', 'email', 'first_name',)
    search_fields = ('username', 'email', 'first_name',)
