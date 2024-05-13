# Generated by Django 3.2 on 2024-05-13 15:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(32000, message='Количество не может быть больше 32 000'), django.core.validators.MinValueValidator(1, message='Количество не может быть меньше 1')], verbose_name='Количество'),
        ),
    ]
