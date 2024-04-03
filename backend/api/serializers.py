from djoser.serializers import UserSerializer as DjoserUserSerializer
from djoser.conf import settings

from django.db import connection, reset_queries

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.validators import UnicodeUsernameValidator

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
)


User = get_user_model()


# class UserSerializer(DjoserUserSerializer):
class UserSerializer(serializers.Serializer):
    username = CharField(
        max_length=150,
        read_only=True,
    )
    first_name = CharField(
        max_length=150,
        read_only=True,
    )
    last_name = CharField(
        max_length=150,
        read_only=True,
    )
    email = EmailField(
        max_length=150,
        read_only=True
    )

    # is_subscribed = serializers.SerializerMethodField(read_only=True)

    # def get_is_subscribed(self, obj):  # obj - экземпляр Note
    #     user = serializers.CurrentUserDefault()
    #     if obj:
    #         return obj.marks.split(', ')
    #     return []

    # class Meta:
    #     model = User
    #     fields = tuple(User.REQUIRED_FIELDS) + (
    #         settings.USER_ID_FIELD,
    #         settings.LOGIN_FIELD,
    #     )
    #     read_only_fields = (settings.LOGIN_FIELD,)


# class UserSerializer(Serializer):
#     email = EmailField(
#         max_length=150,
#         required=True,
#     )
#     email = EmailField(
#         max_length=150,
#         required=True,
#     )
#     email = EmailField(
#         max_length=150,
#         required=True,
#     )
#     email = EmailField(
#         max_length=150,
#         required=True,
#     )
#     username = CharField(
#         max_length=150,
#         required=True,
#         validators=[
#             UnicodeUsernameValidator(),
#             #   validate_username
#         ],
#     )

    # def validate(self, data):
    #     username = data["username"]
    #     email = data["email"]
    #     user_on_email = User.objects.filter(email=email).first()
    #     user_on_username = User.objects.filter(username=username).first()
    #     if user_on_email != user_on_username:
    #         error_msg = {}
    #         if user_on_username:
    #             error_msg['username'] = settings.IS_USER_WITH_THIS_USERNAME
    #         if user_on_email:
    #             error_msg['email'] = settings.IS_USER_WITH_THIS_EMAIL
    #         raise ValidationError(error_msg)
    #     return data

    # def save(self):
    #     username = self.validated_data["username"]
    #     email = self.validated_data["email"]
    #     user, _ = User.objects.get_or_create(
    #         username=username, email=email
    #     )
    #     confirmation_code = default_token_generator.make_token(user)
    #     send_email_confirmation_code(
    #         confirmation_code=confirmation_code,
    #         email=user.email,
    #     )
    #     return self.validated_data
