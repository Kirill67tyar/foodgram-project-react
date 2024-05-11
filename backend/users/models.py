from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


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
        help_text=f'Обязательное. Количество символов <= {150}',
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
    following = models.ManyToManyField(
        to='self',
        through='users.Follow',
        related_name='followers',
        symmetrical=False,
        verbose_name='Подписан на'
    )
    favorites = models.ManyToManyField(
        to='recipes.Recipe',
        through='users.Favorite',
        related_name='in_favorites',
        verbose_name='Рецепты в избранном'
    )

    class Meta:
        ordering = (
            'username',
            '-date_joined',
        )

    def __str__(self):
        return f'username: {self.username}'


class Follow(models.Model):
    from_user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Пользователь подписан'
    )
    to_user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='from_subscribed',
        verbose_name='На пользователя подписан'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user', ],
                name='unique_key_user_following'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(from_user=models.F('to_user')),
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ],
                name='unique_key_user_recipe'
            ),
        ]
