from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

# # Теги для рецептов (завтрак, обед, ужин) - many to many
# # Подписки на пользователей - many to many
# # Добавление рецепта в избранное - many to many

# # Рецепт по отношению к автору - foreign key


# # фронт приложения:
# # http://localhost/

# # спецификацию (доки) API:
# # http://localhost/api/docs/redoc.html


class Recipe(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название рецепта',
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    minutes = models.PositiveSmallIntegerField(
        verbose_name='Минут готовить'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
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
        verbose_name='Ингредиенты'
    )


class Ingredient(models.Model):
    # MEASUREMENT_UNIT_CHOICES = ()

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название ингредиента',
    )
    
    measure = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Мера измерения",
    )
    """
    -- Ингредиент
    Данные об ингредиентах должны храниться в нескольких связанных таблицах. На стороне пользователя ингредиент должен содержать следующие атрибуты:
        Название.
        Количество.
        Единицы измерения.
    Все поля обязательны для заполнения.
    """
    pass
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )



class Tag(models.Model):
    """
    -- Тег
    Атрибуты модели:
        Название.
        Цветовой код, например, #49B64E.
        Slug.
    Все поля обязательны для заполнения и уникальны.
    """
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
        related_name='recipes',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tags',
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


# class Order(models.Model):
#     owner = ...
#     pass


# """
# -- Рецепт
# Атрибуты модели:
#     Автор публикации (пользователь).
#     Название.
#     Картинка.
#     Текстовое описание.
#     Ингредиенты — продукты для приготовления блюда по рецепту. Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения.
#     Тег. Можно установить несколько тегов на один рецепт.
#     Время приготовления в минутах.
# Все поля обязательны для заполнения.

# -- Тег
# Атрибуты модели:
#     Название.
#     Цветовой код, например, #49B64E.
#     Slug.
# Все поля обязательны для заполнения и уникальны.

# -- Ингредиент
# Данные об ингредиентах должны храниться в нескольких связанных таблицах. На стороне пользователя ингредиент должен содержать следующие атрибуты:
#     Название.
#     Количество.
#     Единицы измерения.
# Все поля обязательны для заполнения.
# """
    """
    -- Рецепт
    Атрибуты модели:
        Автор публикации (пользователь).
        Название.
        Картинка.
        Текстовое описание.
        Ингредиенты — продукты для приготовления блюда по рецепту. Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения.
        Тег. Можно установить несколько тегов на один рецепт.
        Время приготовления в минутах.
    Все поля обязательны для заполнения.

    
g               "г": 1668,
cup             "стакан": 41,
taste           "по вкусу": 104,
tablespoon      "ст. л.": 67,
item            "шт.": 114,
milliliter      "мл": 31,
tea spoon      "ч. л.": 47,
drop   "капля": 4,
star   "звездочка": 1,
pinch   "щепотка": 12,
handful   "горсть": 15,
piece   "кусок": 8,
kg   "кг": 26,
packet   "пакет": 5,
bunch   "пучок": 4,
slice   "долька": 1,
jar   "банка": 9,
package   "упаковка": 11,
clove   "зубчик": 1,
layer   "пласт": 1,
pack   "пачка": 1,
carcass   "тушка": 3,
pod   "стручок": 2,
twig   "веточка": 4,
bottle   "бутылка": 2,
L   "л": 1,
loaf   "батон": 1,
bag   "пакетик": 2,
leaf   "лист": 1,
stem   "стебель": 1
    """
