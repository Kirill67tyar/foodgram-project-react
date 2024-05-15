from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram_backend import constants


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        blank=False,
        unique=True,
        verbose_name='email',
    )
    first_name = models.CharField(
        max_length=constants.MAX_LENGTH_USER_NAME,
        blank=False,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=constants.MAX_LENGTH_USER_NAME,
        blank=False,
        verbose_name='Фамилия',
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
