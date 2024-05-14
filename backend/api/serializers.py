import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import Http404
from rest_framework import serializers
from rest_framework.serializers import Serializer, ValidationError

from foodgram_backend import constants
from recipes.models import (Favorite, Ingredient, Order, Recipe,
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


class UserAuthorSubscribeSerializer(serializers.Serializer):
    user_to_follow = serializers.IntegerField()

    def validate(self, data):
        err_msg = {}
        request = self.context['request']
        user = self.context['user']
        user_to_follow = self.context['user_to_follow']
        user_in_following = Follow.objects.filter(
            from_user=user,
            to_user=user_to_follow).exists()
        if request.method == 'POST':
            if user_in_following:
                err_msg['Ошибка'] = 'вы уже подписаны на этого пользователя'
                raise ValidationError(
                    err_msg
                )
            if user_to_follow == user:
                err_msg['Ошибка'] = 'нельзя подписаться на самого себя'
                raise ValidationError(
                    err_msg
                )
        else:
            if not user_in_following:
                err_msg['Ошибка'] = 'вы не подписаны на этого пользователя'
                raise ValidationError(
                    err_msg
                )
        return data

    def save(self):
        Follow.objects.create(
            from_user=self.context['user'],
            to_user=self.context['user_to_follow'],
        )
        return self.validated_data

    def delete(self):
        Follow.objects.filter(
            from_user=self.context['user'],
            to_user=self.context['user_to_follow'],
        ).delete()
        return self.validated_data

    def to_representation(self, value):
        user_to_follow = self.context['user_to_follow']
        serializer = UserSubscriptionsModelSerializer(user_to_follow)
        serializer.context['request'] = self.context['request']
        return serializer.data


class AddToFavoriteSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    recipe = serializers.IntegerField()

    def validate(self, data):
        user = User.objects.get(pk=data['user'])
        recipe = Recipe.objects.filter(pk=data['recipe']).first()
        request = self.context['request']
        err_msg = {}
        if not recipe:
            if request.method == 'POST':
                err_msg['Ошибка'] = 'рецепт отсутствует'
                raise ValidationError(err_msg)
            raise Http404('Рецепт не найден.')
        recipe_in_favorite = Favorite.objects.filter(
            user=user,
            recipe=recipe,
        ).exists()
        if self.context['request'].method == 'POST':
            if recipe_in_favorite:
                err_msg['Ошибка'] = 'Рецепт добавлен в избранное'
                raise ValidationError(err_msg)
        else:
            if not recipe_in_favorite:
                err_msg['Ошибка'] = 'Рецепта нет в избранном'
                raise ValidationError(err_msg)
        return data

    def save(self):
        user = User.objects.get(pk=self.validated_data['user'])
        recipe = Recipe.objects.get(pk=self.validated_data['recipe'])
        # user.favorites.add(recipe)
        Favorite.objects.create(
            user=user,
            recipe=recipe,
        )
        return self.validated_data

    def delete(self):
        user = User.objects.get(pk=self.validated_data['user'])
        recipe = Recipe.objects.get(pk=self.validated_data['recipe'])
        Favorite.objects.filter(
            user=user,
            recipe=recipe,
        ).delete()
        return self.validated_data

    def to_representation(self, value):
        recipe_pk = value['recipe']
        recipe = Recipe.objects.get(pk=recipe_pk)
        serializer = RecipeToFavoriteModelSerializer(recipe)
        serializer.context['request'] = self.context['request']
        return serializer.data


class AddToShoppingCart(serializers.Serializer):
    recipe = serializers.IntegerField()
    order = serializers.IntegerField()

    def validate(self, data):
        recipe = Recipe.objects.filter(pk=data['recipe']).first()
        order = Order.objects.filter(pk=data['order']).first()
        request = self.context['request']
        err_msg = {}
        if not recipe:
            if request.method == 'POST':
                err_msg['Ошибка'] = 'рецепт отсутствует'
                raise ValidationError(err_msg)
            raise Http404('Рецепт не найден.')
        recipe_in_order_for_current_user = order.recipe.filter(
            pk=recipe.pk).exists()
        if request.method == 'POST':
            if not recipe_in_order_for_current_user:
                return data
            err_msg['Ошибка'] = 'Заказ уже добавлен в корзину'
            raise ValidationError(
                err_msg
            )
        else:
            if not recipe_in_order_for_current_user:
                err_msg['Ошибка'] = 'Заказ уже добавлен в корзину'
                raise ValidationError(
                    err_msg
                )
        return data

    def save(self):
        recipe = Recipe.objects.get(pk=self.validated_data['recipe'])
        order = Order.objects.get(pk=self.validated_data['order'])
        order.recipe.add(recipe)
        return self.validated_data

    def delete(self):
        recipe = Recipe.objects.get(pk=self.validated_data['recipe'])
        order = Order.objects.get(pk=self.validated_data['order'])
        order.recipe.remove(recipe)
        return self.validated_data

    def to_representation(self, value):
        recipe_pk = value['recipe']
        recipe = Recipe.objects.get(pk=recipe_pk)
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
            and self.context['request'].user.orders.filter(
                downloaded=False
            ).exists()
            and Order.objects.filter(
                recipe=obj,
                owner=self.context['request'].user,
                downloaded=False,
            ).exists()
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

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise ValidationError(
                {'tags': 'Повторяющиеся поля', }
            )
        return value

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        err_msg = {}
        if not ingredients_data:
            err_msg['ingredients'] = [constants.INGREDIENTS_REQUIRED_FIELD]
            raise ValidationError(
                err_msg
            )
        ingredients_ids = [ingredient['id'] for ingredient in ingredients_data]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            err_msg['ingredients'] = [constants.REPEATED_INGREDIENTS]
            raise ValidationError(
                err_msg
            )
        ingredients_ids_exists = list(
            Ingredient.objects.filter(
                id__in=ingredients_ids).values_list('id', flat=True)
        )
        ingredients_ids.sort()
        ingredients_ids_exists.sort()
        if ingredients_ids != ingredients_ids_exists:
            err_msg['ingredients'] = [constants.NON_EXISTENT_ELEMENTS]
            raise ValidationError(
                err_msg
            )
        tags_ids = data.get('tags')
        if not tags_ids:
            err_msg['tags'] = [constants.TAGS_REQUIRED_FIELD]
            raise ValidationError(
                err_msg
            )
        if len(tags_ids) != len(set(tags_ids)):
            err_msg['tags'] = [constants.REPEATED_TAGS]
            raise ValidationError(
                err_msg
            )
        return data

    def add_ingredients_to_recipe(self, ingredients_data, recipe):
        ingredients_ids = {
            ingredient['id']: ingredient for ingredient in ingredients_data}
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    amount=ingredients_ids[ingredient_id]['amount']
                )
                for ingredient_id in ingredients_ids
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
