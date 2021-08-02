from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import connection
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from caravel.settings import MEDIA_ROOT, MEDIA_URL
from caravel.utils import dictfetchall
from rooms.models import User
from .forms import SignUpForm
from django.core.files.storage import FileSystemStorage
import re


def login_user(request):
    if request.user.is_authenticated:
        redirect('index')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return show_profile(request, user.login)
        else:
            context = {
                'error': True
            }
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html')


def sign_up(request):
    if request.user.is_authenticated:
        redirect('index')

    context = {}

    if request.method == 'POST':
        errors = {}
        name = request.POST['name'].strip()
        surname = request.POST['surname'].strip()
        user_login = request.POST['login'].strip()
        if not re.match(r'^[a-zA-Z0-9_.-]{3,24}$', user_login):
            errors['login'] = {}
            errors['login']['validation'] = True
        elif not User.check_login_uniqueness(user_login):
            errors['login'] = {}
            errors['login']['uniqueness'] = True

        email = request.POST['email'].strip()
        if not re.match(r'^([a-zA-Z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6})$', email):
            errors['email'] = {}
            errors['email']['validation'] = True
        elif not User.check_email_uniqueness(email):
            errors['email'] = {}
            errors['email']['uniqueness'] = True

        phone_number = request.POST['phone_number'].strip()
        if not re.match(r'^\+?[0-9]{3}-?[0-9]{6,12}$', phone_number):
            errors['phone_number'] = {}
            errors['phone_number']['validation'] = True
        elif not User.check_phone_number_uniqueness(phone_number):
            errors['phone_number'] = {}
            errors['phone_number']['uniqueness'] = True

        password1 = request.POST['password1']
        if not re.match(r'^(?=.*?[a-zA-Z0-9#?!@$ %^&*-]).{8,}$', password1):
            errors['password1'] = True

        password2 = request.POST['password2']
        if password1 != password2:
            errors['password2'] = True

        if len(errors) != 0:
            context['errors'] = errors
            return render(request, 'signup.html', context)

        password = make_password(password1)
        mail_status = -1
        message = f'Приветствуем, {name}.\n\nВы успешно зарегистрировались на CaravelHotel.ua.\nВы можете войти в свой аккаунт перейдя по ссылке: http://127.0.0.1:8000/accounts/login.'

        cursor = connection.cursor()
        cursor.execute('insert into rooms_user(name, surname, login, password, email, phone_number, is_superuser, is_active, is_staff) values (%s, %s, %s, %s, %s, %s, false, true, false);', [name, surname, user_login, password, email, phone_number])
        user_id = cursor.lastrowid

        mail_status = send_mail(
            subject=f'Добро пожаловать, {user_login}!',
            message=message,
            from_email='CaravelHotel.ua',
            recipient_list=[email],
            fail_silently=True
            )
        mail_status += 1

        cursor.execute('insert into rooms_notification(message, status_id, user_id) values (%s, %s, %s);', [message, mail_status, user_id])
        context['sign_up_message'] = True

    return render(request, 'signup.html', context)


def show_profile(request, user_login, context=None):
    user = request.user.login
    if user_login != user:
        return redirect('index')
    else:
        if context:
            return render(request, 'profile.html', context)
        else:
            return render(request, 'profile.html')


def change_info(request, user_login, context=None):
    if user_login != request.user.login:
        redirect('index')
    user_information = dictfetchall(connection.cursor().execute('select id, name, surname, login, password, email, phone_number from rooms_user where login = %s', [user_login]))[0]
    if not context:
        context = {}
    context['current_user'] = user_information
    if request.method == 'POST':
        errors = {}
        new_name = request.POST['name'].strip()
        new_surname = request.POST['surname'].strip()
        new_email = request.POST['email'].strip()
        if not re.match(r'^([a-zA-Z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6})$', new_email):
            errors['email'] = {}
            errors['email']['validation'] = True
        # elif not User.check_email_uniqueness(new_email):
        #     errors['email'] = {}
        #     errors['email']['uniqueness'] = True

        new_phone_number = request.POST['phone_number'].strip()
        if not re.match(r'^\+?[0-9]{3}-?[0-9]{6,12}$', new_phone_number):
            errors['phone_number'] = {}
            errors['phone_number']['validation'] = True
        # elif not User.check_phone_number_uniqueness(new_phone_number):
        #     errors['phone_number'] = {}
        #     errors['phone_number']['uniqueness'] = True

        new_login = request.POST['login'].strip()
        if not re.match(r'^[a-zA-Z0-9_.-]{3,24}$', new_login):
            errors['login'] = {}
            errors['login']['validation'] = True
        # elif not User.check_login_uniqueness(new_login):
        #     errors['login'] = {}
        #     errors['login']['uniqueness'] = True

        new_password1 = request.POST['password1']
        new_password2 = request.POST['password2']
        if new_password1 and new_password2:
            if not re.match(r'^(?=.*?[a-zA-Z0-9#?!@$ %^&*-]).{8,}$', new_password1):
                errors['password1'] = True
            if new_password1 != new_password2:
                errors['password2'] = True

        if len(errors) != 0:
            context['errors'] = errors
            return render(request, 'signup.html', context)

        password = make_password(new_password1)
        mail_status = -1

        query = 'update rooms_user set'
        arguments = []
        if new_name != user_information['name']:
            arguments.append(new_name)
            query += ' name=%s'
        if new_surname != user_information['surname']:
            arguments.append(new_surname)
            query += ' ' if query[-1] != 's' else ','
            query += 'surname=%s'
        if new_email != user_information['email']:
            arguments.append(new_email)
            query += ' ' if query[-1] != 's' else ','
            query += 'email=%s'
        if new_phone_number != user_information['phone_number']:
            arguments.append(new_phone_number)
            query += ' ' if query[-1] != 's' else ','
            query += 'phone_number=%s'
        if new_login != user_information['login']:
            arguments.append(new_login)
            query += ' ' if query[-1] != 's' else ','
            query += 'login=%s'
        if new_password1 and new_password2:
            arguments.append(password)
            query += ' ' if query[-1] != 's' else ','
            query += 'password=%s'

        if not arguments:
            context['data_not_changed'] = True
            return render(request, 'change_info.html', context)

        query += ' where id = %s'
        arguments.append(user_information['id'])

        # query = 'update rooms_user set name=%s, surname=%s, email=%s, phone_number=%s, login=%s'
        # arguments = [new_name, new_surname, new_email, new_phone_number, new_login]
        # if new_password1 and new_password2:
        #     query += ', password=%s'
        #     arguments.append(password)
        # query += ' where id=%s'
        # arguments.append(user_information['id'])

        cursor = connection.cursor()
        cursor.execute(query, arguments)
        user_id = user_information['id']

        message = f'Приветствуем, {new_name}.\n\nВы успешно изменили данные своего профиля на CaravelHotel.ua.'
        mail_status = send_mail(
            subject=f'Данные профиля изменены!',
            message=message,
            from_email='CaravelHotel.ua',
            recipient_list=[user_information['email']],
            fail_silently=True
            )
        mail_status += 1

        cursor.execute('insert into rooms_notification(message, status_id, user_id) values (%s, %s, %s);', [message, mail_status, user_id])

        context = {
            'data_changed_success': True,
        }
        if new_password1 and new_password2:
            return redirect('index')
        return redirect('show_profile', new_login)
    else:
        return render(request, 'change_info.html', context)
