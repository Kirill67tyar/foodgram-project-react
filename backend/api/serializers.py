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
    ListField,
)

from orders.models import RecipeOrder
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    RecipeTag,
)


User = get_user_model()


class RecipeToFavoriteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


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
        a = 1
        user = self.context['request'].user
        if user.is_authenticated:
            return user in obj.following.all()
        return False
        # return user in obj.followers.all()


class UserModelSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        a = 1
        user = self.context['request'].user
        return user in obj.following.all()
        # return user in obj.followers.all()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class UserSubscriptionsModelSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        a = 1
        user = self.context['request'].user
        return user in obj.following.all()
        # return user in obj.followers.all()

    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    recipes = RecipeToFavoriteModelSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


class ThinTagModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',)
        # extra_kwargs = {'id': {'write_only': True}}


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
    author = UserSerializer(  # UserModelSerializer
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

    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            order = user.orders.filter(downloaded=False).first()
            if order:
                return RecipeOrder.objects.filter(
                    recipe=obj,
                    order=order,
                ).exists()
        return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
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


class ThinRecipeIngredientSerializer(Serializer):
    id = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=9223372036854775807,
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=32767,
    )


class RecipeWriteModelSerializer(serializers.ModelSerializer):

    # tags = ThinTagModelSerializer(
    #     required=True,
    #     many=True,
    # )
    tags = ListField(
        # required=True,
        # many=True,
    )
    ingredients = ThinRecipeIngredientSerializer(
        required=True,
        many=True
    )
    # image - https://github.com/Kirill67tyar/kittygram_backend/blob/main/cats/serializers.py#L32
    image = Base64ImageField(
        required=True,
        allow_null=True,
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

    def create(self, validated_data):
        tags_ids = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        ingredients_ids = {
            ingredient['id']: ingredient for ingredient in ingredients_data}
        recipe = Recipe.objects.create(**validated_data)
        #! под вопросом насчёт list
        tags = list(Tag.objects.filter(id__in=tags_ids))
        ingredients = list(Ingredient.objects.filter(
            id__in=ingredients_ids.keys()))
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredients_ids[ingredient.pk]['amount']
                )
                for ingredient in ingredients
            ]
        )
        return recipe

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        tags_ids = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        ingredients_ids = {
            ingredient['id']: ingredient for ingredient in ingredients_data
        }
        tags_lst = list(Tag.objects.filter(id__in=tags_ids))
        instance.tags.clear()
        instance.tags.set(tags_lst)

        ingredients_lst = list(Ingredient.objects.filter(
            id__in=ingredients_ids.keys()))
        instance.ingredients.clear()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredients_ids[ingredient.pk]['amount']
                )
                for ingredient in ingredients_lst
            ]
        )
        instance.save()
        return instance

    def to_representation(self, value):
        serializer = RecipeReadModelSerializer(value)
        serializer.context['request'] = self.context['request']
        return serializer.data
