import base64

from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.serializers import ListField, Serializer, ValidationError

from users.models import Follow
from orders.models import RecipeOrder
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

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
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        return bool(
            self.context.get('request')
            and self.context['request'].user.is_authenticated
            and self.context['request'].user in obj.following.all()
        )


class UserSubscriptionsModelSerializer(UserModelSerializer):

    class Meta(UserModelSerializer.Meta):
        fields = UserModelSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    recipes = RecipeToFavoriteModelSerializer(many=True, read_only=True)

    recipes_count = serializers.SerializerMethodField(read_only=True)

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
            self.context['user'].following.add(self.context['user_to_follow'])
            return self.validated_data
        
        def delete(self):
            self.context['user'].following.remove(self.context['user_to_follow'])
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
                raise ValidationError(err_msg, code=status.HTTP_404_NOT_FOUND)
            recipe_in_favorite = user.favorites.filter(
                favorite__recipe=recipe).exists()
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
            user.favorites.add(recipe)
            return self.validated_data
        
        def delete(self):
            user = User.objects.get(pk=self.validated_data['user'])
            recipe = Recipe.objects.get(pk=self.validated_data['recipe'])
            user.favorites.remove(recipe)
            return self.validated_data
        
        def to_representation(self, value):
            # a = 1
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
        return bool(
            self.context.get('request')
            and self.context['request'].user.is_authenticated
            and obj in self.context['request'].user.favorites.all()
        )

    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request')
            and self.context['request'].user.is_authenticated
            and self.context['request'].user.orders.filter(
                downloaded=False
            ).exists()
            and RecipeOrder.objects.filter(
                recipe=obj,
                order=self.context['request'].user.orders.filter(
                    downloaded=False).first(),
            ).exists()
        )

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

# class ThinRecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         queryset=Recipe.objects.all(),
#         many=False,
#         read_only=False,
#     )
#     # id = serializers.IntegerField(
#     #     required=True,
#     #     min_value=1,
#     #     max_value=9223372036854775807,
#     # )
#     # amount = serializers.IntegerField(
#     #     required=True,
#     #     min_value=1,
#     #     max_value=32767,
#     # )
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount',)


class RecipeWriteModelSerializer(serializers.ModelSerializer):

    # tags = ListField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        # read_only=False,
        # pk_field='id',
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
        if not data.get('tags'):
            err_msg['tags'] = [settings.REQUIRED_FIELD]
            raise ValidationError(
                err_msg
            )

        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        ingredients_ids = {
            ingredient['id']: ingredient for ingredient in ingredients_data}
        recipe = Recipe.objects.create(**validated_data)
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
        # tags_ids = validated_data.pop('tags')
        tags_lst = validated_data.pop('tags')  # !
        ingredients_data = validated_data.pop('ingredients')
        ingredients_ids = {
            ingredient['id']: ingredient for ingredient in ingredients_data
        }
        # tags_lst = list(Tag.objects.filter(id__in=tags_ids))
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
