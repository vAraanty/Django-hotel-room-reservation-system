from django.db import models, connection
from django.core import validators
from django.urls import reverse
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from caravel.utils import dictfetchall
# Create your models here.


class Room(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)], default=1, verbose_name='Цена')
    exists = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)], verbose_name='Всего номеров')
    adult_capacity = models.PositiveIntegerField(verbose_name='Вместительность взрослых')
    child_capacity = models.PositiveIntegerField(verbose_name='Вместительность детей')
    area = models.FloatField(validators=[validators.MinValueValidator(0)], verbose_name='Площадь')

    class Meta:
        verbose_name = 'комната'
        verbose_name_plural = 'комнаты'

    def get_absolute_url(self):
        return reverse('show_room', kwargs={'room_id': self.pk})

    def __str__(self):
        return self.name


    @staticmethod
    def get_name_by_id(find_id):
        cursor = connection.cursor()
        raw_query = cursor.execute('select name from rooms_room where id = %s', [find_id]).fetchone()[0]
        return raw_query


class RoomImage(models.Model):
    room = models.ForeignKey(Room, models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')


class Guest(models.Model):
    name = models.CharField(max_length=15, verbose_name='Имя')
    surname = models.CharField(max_length=30, verbose_name='Фамилия')
    email = models.CharField(max_length=60, verbose_name='Email', validators=[validators.validate_email])
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона',
                                    validators=[validators.RegexValidator(regex=r'^\+?[0-9]{3}-?[0-9]{6,12}$',
                                                                          message='Проверьте правильность номера. Номер должен начинаться с + и состоять из цифр.')])

    def __str__(self):
        return f'{self.name} {self.surname}, {self.email}'

    class Meta:
        verbose_name = 'гость'
        verbose_name_plural = 'гости'

    @staticmethod
    def get_guest_description_by_id(find_id):
        cursor = connection.cursor()
        raw_query = cursor.execute('select name, surname, email, phone_number from rooms_guest where id = %s', [find_id])
        fetched = dictfetchall(raw_query)[0]
        return fetched


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=15, verbose_name='Имя')
    surname = models.CharField(max_length=30, verbose_name='Фамилия')
    login = models.CharField(max_length=20, verbose_name='Имя пользователя', unique=True,
                             validators=[validators.RegexValidator(regex=r'^[a-zA-Z0-9_.-]{3,24}$',
                                                                  message='Недопустимые символы, доступны только буквы латиницы, цифры, - и _.')])
    password = models.CharField(max_length=64, verbose_name='Пароль')
    email = models.CharField(max_length=60, verbose_name='Email', unique=True, validators=[validators.validate_email])
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона', unique=True,
                                    validators=[validators.RegexValidator(regex=r'^\+?[0-9]{3}-?[0-9]{6,12}$',
                                                                          message='Проверьте правильность номера. Номер должен начинаться с + и состоять из цифр.')])
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Менеджер')
    is_superuser = models.BooleanField(default=False, verbose_name='Администратор')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'login', 'phone_number']

    objects = UserManager()

    def __str__(self):
        return f'{self.name} {self.surname}, {self.email}'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def get_short_name(self):
        return f'{self.email}'

    def get_user_bookings_raw(self):
        cursor = connection.cursor()
        query_cursor = cursor.execute('select * from rooms_RequestReservation where user_id = %s', [self.pk])
        return query_cursor

    def get_user_bookings_raw_dict(self):
        raw_query_dict = dictfetchall(self.get_user_bookings_raw())
        return raw_query_dict

    def get_user_bookings(self):

        raw_query = self.get_user_bookings_raw_dict()
        results = []
        for query in raw_query:
            temp_dict = {
                'room': Room.get_name_by_id(query['room_id']),
                'arrival_date': query['arrival_date'],
                'departure_date': query['departure_date'],
                'status': RequestReservationStatus.get_name_by_id(query['status_id'])
            }
            results.append(temp_dict)
        return results

    @staticmethod
    def get_user_description_by_id(find_id):
        cursor = connection.cursor()
        raw_query = cursor.execute('select name, surname, email, phone_number from rooms_user where id = %s', [find_id])
        fetched = dictfetchall(raw_query)[0]
        return fetched

    def count_bookings_waiting_for_payment(self):
        counter = 0
        raw_bookings = self.get_user_bookings_raw_dict()
        for booking in raw_bookings:
            if booking['status_id'] == 2:
                counter += 1
        return counter

    @staticmethod
    def check_phone_number_uniqueness(ph_num_to_check):
        raw_query = connection.cursor().execute('select phone_number from rooms_user where phone_number = %s', [ph_num_to_check]).fetchone()
        return not bool(raw_query)

    @staticmethod
    def check_email_uniqueness(email_to_check):
        raw_query = connection.cursor().execute('select email from rooms_user where email = %s', [email_to_check]).fetchone()
        return not bool(raw_query)

    @staticmethod
    def check_login_uniqueness(login_to_check):
        raw_query = connection.cursor().execute('select login from rooms_user where login = %s', [login_to_check]).fetchone()
        return not bool(raw_query)


class RequestReservationStatus(models.Model):
    name = models.CharField(max_length=40, verbose_name='Статус', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'статус бронирования'
        verbose_name_plural = 'статусы бронирования'

    @staticmethod
    def get_name_by_id(find_id):
        cursor = connection.cursor()
        raw_query = cursor.execute('select name from rooms_RequestReservationStatus where id = %s', [find_id]).fetchone()[0]
        return raw_query


class RequestReservation(models.Model):
    room = models.ForeignKey(Room, models.PROTECT, verbose_name='Комната')
    arrival_date = models.DateField(verbose_name='Дата заезда')
    departure_date = models.DateField(verbose_name='Дата выезда')
    status = models.ForeignKey(RequestReservationStatus, models.PROTECT, verbose_name='Статус')
    user = models.ForeignKey(User, models.CASCADE, verbose_name='Клиент', null=True, blank=True)
    guest = models.ForeignKey(Guest, models.CASCADE, verbose_name='Гость', null=True, blank=True)
    token = models.CharField(max_length=32, verbose_name='Токен', unique=True)

    def __str__(self):
        return f'{ self.user if self.user is not None else self.guest }, {self.room}, {self.arrival_date}'

    class Meta:
        verbose_name = 'заказ/бронирование'
        verbose_name_plural = 'заказы/бронирования'

    @staticmethod
    def check_token_uniqueness(find_token):
        raw_query = connection.cursor().execute('select token from rooms_RequestReservation where token = %s', [find_token]).fetchone()
        return not bool(raw_query)

    @staticmethod
    def get_reservation_by_token(find_token):
        raw_query = connection.cursor().execute('select * from rooms_RequestReservation where token = %s', [find_token])
        fetched = dictfetchall(raw_query)[0]
        return fetched

    @staticmethod
    def get_when_created_by(find_id):
        raw_query = connection.cursor().execute('select when_changed from rooms_ReservationStatusLog where request_reservation_id = %s and new_status_id = 1;', [find_id]).fetchall()[0][0]
        return raw_query


class Receipt(models.Model):
    reservation = models.ForeignKey(RequestReservation, models.CASCADE, verbose_name='Бронирование')
    receipt = models.FileField(verbose_name='Квитанция', upload_to='receipts/')

    class Meta:
        verbose_name = 'квитанция'
        verbose_name_plural = 'квитанции'


class NotificationStatus(models.Model):
    name = models.CharField(max_length=40, verbose_name='Статус', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'статус оповещения'
        verbose_name_plural = 'статусы оповещения'


class Notification(models.Model):
    message = models.TextField(verbose_name='Текст уведомления')
    status = models.ForeignKey(NotificationStatus, models.PROTECT, verbose_name='Статус')
    request_reservation = models.ForeignKey(RequestReservation, models.CASCADE, null=True, verbose_name='Броинрование')
    user = models.ForeignKey(User, models.CASCADE, verbose_name='Пользователь', null=True)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'оповещение'
        verbose_name_plural = 'оповещения'


class ReservationStatusLog(models.Model):
    request_reservation = models.ForeignKey(RequestReservation, models.CASCADE, verbose_name='Бронирование')
    when_changed = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    new_status = models.ForeignKey(RequestReservationStatus, models.PROTECT, verbose_name='Новый статус')

    class Meta:
        verbose_name = 'изменение статуса'
        verbose_name_plural = 'изменения статуса'

