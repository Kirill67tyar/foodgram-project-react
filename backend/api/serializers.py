import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import ListField, Serializer, ValidationError

from orders.models import RecipeOrder
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()


class LimitedRecipeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit')
        if recipes_limit:
            data = data.all()[:int(recipes_limit)]
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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user in obj.following.all()
        return False

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
        user = self.context['request'].user
        return user in obj.following.all()

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

    tags = ListField()
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

    def validate_cooking_time(self, value):
        if value < 1:
            raise ValidationError(
                settings.TIME_ERROR_MSG
            )
        return value

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        err_msg = {}
        if not ingredients_data:
            err_msg['ingredients'] = [settings.REQUIRED_FIELD]
            raise ValidationError(
                err_msg
            )
        ingredients_ids = [ingredient['id'] for ingredient in ingredients_data]
        ingredients_ids_exists = list(
            Ingredient.objects.filter(
                id__in=ingredients_ids).values_list('id', flat=True)
        )
        ingredients_ids.sort()
        ingredients_ids_exists.sort()
        if ingredients_ids != ingredients_ids_exists:
            err_msg['ingredients'] = [settings.NON_EXISTENT_ELEMENTS]
            raise ValidationError(
                err_msg
            )
        tags_ids = data.get('tags')
        if not tags_ids or tags_ids > list(set(tags_ids)):
            err_msg['tags'] = [settings.REQUIRED_FIELD]
            raise ValidationError(
                err_msg
            )
        tag_ids_exists = list(
            Tag.objects.filter(
                id__in=tags_ids).values_list('id', flat=True)
        )
        if tags_ids != tag_ids_exists:
            err_msg['tags'] = [settings.NON_EXISTENT_ELEMENTS]
            raise ValidationError(
                err_msg
            )
        return data

    def create(self, validated_data):
        tags_ids = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        ingredients_ids = {
            ingredient['id']: ingredient for ingredient in ingredients_data}
        recipe = Recipe.objects.create(**validated_data)
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
