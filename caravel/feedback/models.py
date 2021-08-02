from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

from rooms.models import Room, User


class Feedback(models.Model):
    user = models.ForeignKey(User, models.deletion.CASCADE, verbose_name='Пользователь')
    rating = models.IntegerField(verbose_name='Оценка')
    room = models.ForeignKey(Room, models.deletion.PROTECT, verbose_name='Номер')
    content = models.TextField(verbose_name='Отзыв')
    when_given = models.DateTimeField(verbose_name='Когда оставлен', auto_now=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
