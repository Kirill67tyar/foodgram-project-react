from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

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

    def __str__(self):
        return f'Заказ - {self.pk}'


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
