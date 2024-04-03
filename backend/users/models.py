
"""
Подписки на пользователей - many to many
Добавление рецепта в избранное - many to many


Система регистрации и авторизации
В проекте должна быть доступна система регистрации и авторизации пользователей. 
Обязательные поля для пользователя:
    логин,
    пароль,
    email,
    имя,
    фамилия.

Уровни доступа пользователей:
    гость (неавторизованный пользователь),
    авторизованный пользователь,
    администратор
"""

from django.db import models

from recipes.models import Recipe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        verbose_name='Логин',
        unique=True,
        help_text=f'Обязательное. Символов <= {150}',
        validators=[
            username_validator,
        ],
        error_messages={
            'уникальность': 'asdasd',
        },
    )
    email = models.EmailField(
        blank=False,
        unique=True,
        verbose_name='email',
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
    )

    class Meta:
        ordering = (
            'username',
            '-date_joined',
        )

    def __str__(self):
        return f'username: {self.username}; email: {self.email}'


class Follow(models.Model):
    # https://github.com/Kirill67tyar/api_final_yatube/blob/master/yatube_api/posts/models.py
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь подписан'
    )
    following = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='На пользователя подписан'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following', ],
                name='unique_key_user_following'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            ),
        ]

    def __str__(self):
        return f'Пользователь (id {self.user_id}) - Подписчик (id {self.following_id})'


class UserFavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_to_favorite',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ],
                name='unique_key_user_recipe'
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
