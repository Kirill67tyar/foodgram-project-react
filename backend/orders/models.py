from django.db import models

from django.contrib.auth import get_user_model
from recipes.models import (
    Recipe,
    Ingredient,
)


User = get_user_model()


class Order(models.Model):
    owner = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Заказчик',
    )
    downloaded = models.BooleanField(
        default=False,
        verbose_name='Скачан',
    )

class RecipeOrder(models.Model):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Рецепт'
    )


"""
3 этапа:

* 1 - написать эндпоинты для добавления/удаления рецептов в заказе, и чтобы заказ нормально создавался
* 2 - написать алгоритм для складывания и подсчёта ингредиентов, хорошо подойдёт словарь {ингредиент: кол-во}
* 3 - написать обрабочтк, для того чтобы отдавать пдф документ клиенту. При этом должно фиксироваться что заказ скачан,
*     и должен формироваться новый заказ после того, как старый скачан

"""

