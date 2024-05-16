import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend import constants
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow

User = get_user_model()


class LimitedRecipeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit:
            try:
                data = data.all()[:int(recipes_limit)]
            except ValueError:
                pass
        return super().to_representation(data)


class RecipeToFavoriteModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        list_serializer_class = LimitedRecipeSerializer


class UserModelSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

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

    def get_is_subscribed(self, obj):
        return bool(
            self.context.get('request')
            and self.context['request'].user.is_authenticated
            and Follow.objects.filter(
                from_user=obj,
                to_user=self.context['request'].user,
            ).exists()
        )


class UserSubscriptionsModelSerializer(UserModelSerializer):

    recipes = RecipeToFavoriteModelSerializer(many=True, read_only=True)

    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserModelSerializer.Meta):
        fields = UserModelSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserAuthorSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = (
            'from_user',
            'to_user',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('from_user', 'to_user',),
                message=constants.MESSAGE_ERROR_SUBSCRIBE_TWICE
            ),
        ]

    def validate(self, data):
        from_user = data['from_user']
        to_user = data['to_user']
        if from_user == to_user:
            raise ValidationError(
                {'errors': constants.MESSAGE_ERROR_SUBSCRIBE_YOURSELF}
            )
        return data

    def to_representation(self, value):
        serializer = UserSubscriptionsModelSerializer(value.to_user)
        serializer.context['request'] = self.context['request']
        return serializer.data


class AddToFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe',),
                message=constants.MESSAGE_ERROR_RECIPE_ALREADY_IN_FAVORITE
            ),
        ]

    def to_representation(self, value):
        serializer = RecipeToFavoriteModelSerializer(value.recipe)
        serializer.context['request'] = self.context['request']
        return serializer.data



class AddToShoppingCart(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = (
            'recipe',
            'owner',
        )
    def to_representation(self, value):
        recipe = Recipe.objects.get(
            pk=self.initial_data['recipe'][constants.ZERO_INDEX])
        serializer = RecipeToFavoriteModelSerializer(recipe)
        serializer.context['request'] = self.context['request']
        return serializer.data


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

    name = serializers.SerializerMethodField(read_only=True)

    measurement_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeReadModelSerializer(serializers.ModelSerializer):
    author = UserModelSerializer(
        many=False,
    )
    tags = TagModelSerializer(
        read_only=True,
        many=True,
    )
    ingredients = RecipeIngredientModelSerializer(
        read_only=True,
        many=True,
        source='recipeingredient_set',
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)

    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

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

    def get_is_favorited(self, obj):
        return bool(
            self.context.get('request')
            and self.context['request'].user.is_authenticated
            and Favorite.objects.filter(
                user=self.context['request'].user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request')
            and self.context['request'].user.is_authenticated
            and Cart.objects.filter(
                recipe=obj,
                owner=self.context['request'].user,
            ).exists()
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ThinRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeWriteModelSerializer(serializers.ModelSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = ThinRecipeIngredientSerializer(
        required=True,
        many=True
    )
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

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        if not ingredients_data:
            raise ValidationError(
                {'ingredients': constants.INGREDIENTS_REQUIRED_FIELD}
            )
        ingredients_lst = [ingredient['id'] for ingredient in ingredients_data]
        if len(ingredients_lst) != len(set(ingredients_lst)):
            raise ValidationError(
                {'ingredients': constants.REPEATED_INGREDIENTS}
            )
        tags_ids = data.get('tags')
        if not tags_ids:
            raise ValidationError(
                {'tags': constants.TAGS_REQUIRED_FIELD}
            )
        if len(tags_ids) != len(set(tags_ids)):
            raise ValidationError(
                {'tags': constants.REPEATED_TAGS}
            )
        return data

    def add_ingredients_to_recipe(self, ingredients_data, recipe):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients_data
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients_to_recipe(
            ingredients_data,
            recipe
        )
        return recipe

    def update(self, instance, validated_data):
        tags_lst = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.add_ingredients_to_recipe(
            ingredients_data,
            instance
        )
        instance.tags.clear()
        instance.tags.set(tags_lst)
        return super().update(instance, validated_data)

    def to_representation(self, value):
        serializer = RecipeReadModelSerializer(value)
        serializer.context['request'] = self.context['request']
        return serializer.data
