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
        verbose_name='Минут готовить'
    )
    image = models.ImageField(
        upload_to='recipes/images/'
    )
    tags = models.ManyToManyField(
        'recipes.Tag',
        through='recipes.RecipeTag',
        related_name='recipes',
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        'recipes.Ingredient',
        through='recipes.RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )


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
        verbose_name='Количество'
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
    color = models.CharField(
        max_length=16
    )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag', ],
                name='unique_key_recipe_tag'
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
