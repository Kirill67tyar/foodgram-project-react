import base64

from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.conf import settings

from django.core.files.base import ContentFile
from django.db import connection, reset_queries

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
    IntegerField,
)

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
)


User = get_user_model()


# class UserSerializer(DjoserUserSerializer):
class UserSerializer(serializers.Serializer):
    email = EmailField(
        max_length=150,
        read_only=True
    )
    id = IntegerField(
        read_only=True
    )
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

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user in obj.following.all()
        # return user in obj.followers.all()


class ThinTagModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
        )
        extra_kwargs = {'id': {'write_only': True}}


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


class RecipeIngredientModelSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField(read_only=True)

    def get_id(self, obj):
        return obj.ingredient.pk
        # return obj.ingredient_id

    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return obj.ingredient.name

    measurement_unit = serializers.SerializerMethodField(read_only=True)

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
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
    # ingredients = IngredientModelSerializer(
    #     read_only=True,
    #     many=True,
    #     source='recipeingredient_set',
    # )
    ingredients = RecipeIngredientModelSerializer(
        read_only=True,
        many=True,
        source='recipeingredient_set',
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj in user.favorites.all()
        return False

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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeWriteModelSerializer(serializers.ModelSerializer):
    """
    {
        "ingredients": [
            {
            "id": 1123,
            "amount": 10
            }
        ],
        "tags": [
            1,
            2
        ],
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
        "name": "string",
        "text": "string",
        "cooking_time": 1
        }
    """
    # image - https://github.com/Kirill67tyar/kittygram_backend/blob/main/cats/serializers.py#L32
    # tags = serializers.SlugRelatedField(
    #     queryset=Tag.objects.all(),
    #     slug_field='id',
    #     many=True,
    # )
    tags = ThinTagModelSerializer(
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=False)
    ingredients = IngredientModelSerializer(
        # required=False,
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
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
