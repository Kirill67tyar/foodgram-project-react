from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        max_length=150,
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
                32000,
                message='Время приготовления не может быть больше 32 000 минут'
            ),
            MinValueValidator(
                1,
                message='Время приготовления не может быть менише 1 минуты'
            )
        ]
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    tags = models.ManyToManyField(
        'recipes.Tag',
        # through='recipes.RecipeTag',
        related_name='recipes',
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        'recipes.Ingredient',
        through='recipes.RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название ингредиента',
    )

    measurement_unit = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Мера измерения",
    )

    class Meta:
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
                32000,
                message='Количество не может быть больше 32 000'
            ),
            MinValueValidator(
                1,
                message='Количество не может быть меньше 1'
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
        max_length=20,
        unique=True,
        verbose_name='Название тега',
    )
    slug = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name='Slug',
    )
    color = ColorField(default='#FF0000')

    def __str__(self):
        return self.name


class Order(models.Model):
    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Заказчик',
    )
    recipe = models.ManyToManyField(
        to=Recipe,
        verbose_name='Рецепты'
    )
    downloaded = models.BooleanField(
        default=False,
        verbose_name='Скачан',
    )
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        default_related_name = 'orders'

    def __str__(self):
        return f'Заказ - {self.pk}'
