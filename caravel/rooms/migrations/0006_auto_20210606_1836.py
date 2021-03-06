# Generated by Django 3.1.7 on 2021-06-06 15:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_requestreservation_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='login',
            field=models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Недопустимые символы, доступны только буквы латиницы, цифры, - и _.', regex='^[a-zA-Z0-9_.-]{3,24}$')], verbose_name='Имя пользователя'),
        ),
    ]
