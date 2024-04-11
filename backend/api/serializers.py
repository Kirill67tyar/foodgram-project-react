from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.conf import settings

from django.db import connection, reset_queries

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
)


User = get_user_model()


# class UserSerializer(DjoserUserSerializer):
class UserSerializer(serializers.Serializer):
    username = CharField(
        max_length=150,
        read_only=True,
    )
    first_name = CharField(
        max_length=150,
        read_only=True,
    )
    last_name = CharField(
        max_length=150,
        read_only=True,
    )
    email = EmailField(
        max_length=150,
        read_only=True
    )

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = serializers.CurrentUserDefault()
        return user in obj.following.all()
        # return user in obj.followers.all()


class TagModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeReadModelSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        # read_only=True,
        many=False,
    )
    tags = TagModelSerializer(
        read_only=True,
        many=True,
    )
    # "is_in_shopping_cart": true,
    ingredients = IngredientModelSerializer(
        read_only=True,
        many=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        print(user)
        return obj in user.favorites.all()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    """
    {
    "id": 0,
    "tags": [
      {
        "id": 0,
        "name": "Завтрак",
        "color": "#E26C2D",
        "slug": "breakfast"
      }
    ],
    "author": {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    },
    "ingredients": [
      {
        "id": 0,
        "name": "Картофель отварной",
        "measurement_unit": "г",
        "amount": 1
      }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "text": "string",
    "cooking_time": 1
  }
    """
    pass

