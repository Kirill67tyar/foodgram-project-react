from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram_backend import constants

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        max_length=constants.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Минут готовить',
        validators=[
            MaxValueValidator(
                constants.MAX_VALUE_FOR_VALIDATOR,
                message=constants.MAX_MESSAGE_VALIDATOR
            ),
            MinValueValidator(
                constants.MIN_VALUE_FOR_VALIDATOR,
                message=constants.MIN_MESSAGE_VALIDATOR
            )
        ]
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    tags = models.ManyToManyField(
        'recipes.Tag',
        related_name='recipes',
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        'recipes.Ingredient',
        through='recipes.RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date', 'name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=constants.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название ингредиента',
    )

    measurement_unit = models.CharField(
        max_length=constants.MAX_LENGTH_NAME,
        db_index=True,
        verbose_name="Мера измерения",
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MaxValueValidator(
                constants.MAX_VALUE_FOR_VALIDATOR,
                message=constants.MAX_MESSAGE_VALIDATOR
            ),
            MinValueValidator(
                constants.MIN_VALUE_FOR_VALIDATOR,
                message=constants.MIN_MESSAGE_VALIDATOR
            )
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient', ],
                name='unique_key_recipe_ingredient'
            ),
        ]


class Tag(models.Model):

    name = models.CharField(
        max_length=constants.MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название тега',
    )
    slug = models.CharField(
        max_length=constants.MAX_LENGTH_NAME,
        unique=True,
        db_index=True,
        verbose_name='Slug',
    )
    color = ColorField(default='#FF0000')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Cart(models.Model):
    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Заказчик',
    )
    recipes = models.ManyToManyField(
        to=Recipe,
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ('pk',)
        default_related_name = 'carts'

    def __str__(self):
        return f'Корзина - {self.pk}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ],
                name='unique_key_user_recipe'
            ),
        ]

    def __str__(self):
        return f'Подписка - {self.pk}'
