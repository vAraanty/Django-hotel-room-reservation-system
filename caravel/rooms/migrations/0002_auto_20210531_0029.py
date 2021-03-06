# Generated by Django 3.1.7 on 2021-05-30 21:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, verbose_name='Администратор'),
        ),
        migrations.AlterField(
            model_name='user',
            name='login',
            field=models.CharField(default='login', max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Недопустимые символы, доступны только буквы латиницы, цифры, - и _.', regex='^[-a-zA-Z0-9_]+$')], verbose_name='Имя пользователя'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='password', max_length=64, verbose_name='Пароль'),
            preserve_default=False,
        ),
    ]
