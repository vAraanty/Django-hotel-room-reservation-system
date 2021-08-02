import secrets

from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db import connection
from django.shortcuts import render, redirect
from django.http import Http404
import re
import datetime

# Create your views here
from accounts.views import show_profile
from caravel.settings import MEDIA_ROOT, MEDIA_URL
from caravel.utils import dictfetchall
from rooms.models import RequestReservation, Room, User, Guest, RequestReservationStatus


def booking_index(request):
    rooms = dictfetchall(connection.cursor().execute('select id, name from rooms_room;'))
    context = {
        'rooms': rooms
    }
    if request.method == 'POST':
        errors = {}
        name = None
        surname = None
        email = None
        phone_number = None
        if request.user.is_anonymous:
            name = request.POST['name'].strip()
            surname = request.POST['surname'].strip()
            email = request.POST['email'].strip()
            if not re.match(r'^([a-zA-Z0-9_\.-]+\@[\da-z\.-]+\.[a-z\.]{2,6})$', email):
                errors['email'] = True

            phone_number = request.POST['phone_number'].strip()
            if not re.match(r'^\+?[0-9]{3}-?[0-9]{6,12}$', phone_number):
                errors['phone_number'] = True
        else:
            name = request.user.name
            surname = request.user.surname
            email = request.user.email
            phone_number = request.user.phone_number

        room = request.POST['room']

        arrival_date = datetime.datetime.strptime(request.POST["arrival_date"].strip(), "%Y-%m-%d")
        if arrival_date < datetime.datetime.now():
            errors['arrival_date'] = True

        departure_date = datetime.datetime.strptime(request.POST["departure_date"].strip(), "%Y-%m-%d")
        if departure_date <= arrival_date or departure_date < datetime.datetime.now():
            errors['departure_date'] = True

        if len(errors) != 0:
            context['errors'] = errors
            return render(request, 'reservation.html', context)

        context['success'] = True

        departure_date = departure_date.date()
        arrival_date = arrival_date.date()

        cursor = connection.cursor()
        token = None
        while True:
            token = secrets.token_urlsafe(24)
            if RequestReservation.check_token_uniqueness(token):
                break

        customer_id = request.user.pk
        if request.user.is_anonymous:
            cursor.execute('insert into rooms_guest(name, surname, email, phone_number) values(%s, %s, %s, %s);', [name, surname, email, phone_number])
            customer_id = cursor.lastrowid
        query = 'insert into rooms_RequestReservation(room_id, arrival_date, departure_date, status_id, '
        query += 'user_id, ' if request.user.is_authenticated else 'guest_id, '
        query += 'token) values(%s, %s, %s, %s, %s, %s);'

        cursor.execute(query, [room, arrival_date, departure_date, 1, customer_id, token])

        message = f'Приветствуем, {name}.\n\nВы забронировали {Room.get_name_by_id(room)} номер. {"Статус бронирования вы можете остлеживать в личном кабинете" if request.user.is_authenticated else ""}.\nПри изменении статуса бронирования Вы будете оповещены на этот email.'
        mail_status = send_mail(
            subject=f'Вы успешно забронировали номер.',
            message=message,
            from_email='CaravelHotel.ua',
            recipient_list=[email],
            fail_silently=True
        )
        mail_status += 1

        reservation_id = cursor.lastrowid
        cursor.execute('insert into rooms_notification(message, status_id, request_reservation_id) values (%s, %s, %s);', [message, mail_status, reservation_id])

    return render(request, 'reservation.html', context)


def show_reservations(request):
    if not request.user.is_staff:
        return redirect('index')
    statuses = dictfetchall(connection.cursor().execute('select * from rooms_RequestReservationStatus'))
    selected = 0
    bookings = None
    if request.method == 'GET' or request.POST['status'] == '0':
        bookings = dictfetchall(connection.cursor().execute('select * from rooms_requestreservation'))
    else:
        status = request.POST['status']
        selected = int(status)
        bookings = dictfetchall(connection.cursor().execute('select * from rooms_requestreservation where status_id = %s', [status]))
    cleaned_bookings = []
    for booking in bookings:
        user_description = None
        if booking['user_id']:
            user_description = User.get_user_description_by_id(booking['user_id'])
        else:
            user_description = Guest.get_guest_description_by_id(booking['guest_id'])
        user_full_name = user_description['name'] + ' ' + user_description['surname']
        user_email = user_description['email']
        user_phone_number = user_description['phone_number']

        cleaned_booking = {
            'id': booking['id'],
            'room': Room.get_name_by_id(booking['room_id']),
            'user': {
                'name': user_full_name,
                'email': user_email,
                'phone_number': user_phone_number
            },
            'arrival_date': booking['arrival_date'],
            'departure_date': booking['departure_date'],
            'status': RequestReservationStatus.get_name_by_id(booking['status_id'])
        }
        cleaned_bookings.append(cleaned_booking)

    context = {
        'bookings': cleaned_bookings,
        'statuses': statuses,
        'selected': selected,
    }
    return render(request, 'show_reservations.html', context)


def change_status(request, reservation_id):
    if not request.user.is_staff:
        redirect('index')

    reservation = dictfetchall(connection.cursor().execute('select * from rooms_requestreservation where id = %s', [reservation_id]))[0]
    statuses = dictfetchall(connection.cursor().execute('select * from rooms_RequestReservationStatus where id > %s', [reservation['status_id']]))

    receipt = None
    fetched = dictfetchall(connection.cursor().execute('select * from rooms_receipt where reservation_id = %s', [reservation_id]))
    if len(fetched):
        receipt = MEDIA_URL + fetched[0]['receipt']

    fetched = dictfetchall(connection.cursor().execute('select when_changed from rooms_ReservationStatusLog where request_reservation_id = %s and new_status_id = 1;', [reservation_id]))
    when_created = 'Ошибка'
    if len(fetched):
        when_created = fetched[0]['when_changed']
    is_user = 'Нет'
    if reservation['user_id']:
        is_user = 'Да'
        user_description = User.get_user_description_by_id(reservation['user_id'])
    else:
        user_description = Guest.get_guest_description_by_id(reservation['guest_id'])
    user_full_name = user_description['name'] + ' ' + user_description['surname']
    user_email = user_description['email']
    user_phone_number = user_description['phone_number']
    cleaned_reservation = {
        'id': reservation['id'],
        'room': Room.get_name_by_id(reservation['room_id']),
        'user': {
            'name': user_full_name,
            'email': user_email,
            'phone_number': user_phone_number,
            'is_user': is_user,
        },
        'when_created': when_created,
        'arrival_date': reservation['arrival_date'],
        'departure_date': reservation['departure_date'],
        'receipt': receipt,
        'status': RequestReservationStatus.get_name_by_id(reservation['status_id'])
    }

    context = {
        'reservation': cleaned_reservation,
        'statuses': statuses,
    }

    if request.method == 'POST':
        new_status = request.POST['new_status']
        new_status_name = RequestReservationStatus.get_name_by_id(new_status)
        connection.cursor().execute('update rooms_RequestReservation set status_id = %s where id = %s', [new_status, cleaned_reservation['id']])

        message = f'Приветствуем, {user_description["name"]}.\n\nСтатус Вашего бронирования {cleaned_reservation["room"]} номера, на даты {cleaned_reservation["arrival_date"]} --- {cleaned_reservation["departure_date"]} был изменён на \"{new_status_name}\".'
        if int(new_status) == 2:
            deadline_date = cleaned_reservation['arrival_date'] - datetime.timedelta(days=4)
            message += f'\n\nОплатите, пожалуйста, бронирование до {deadline_date} включительно, иначе оно будет отклонено.'
            message += '\nПрикрепить квитанцию о оплате Вы можете '
            if reservation['user_id']:
                message += 'в Вашем профиле, или '
            message += f'перейдя по ссылке: http://127.0.0.1:8000/payment/{reservation["token"]}.'
        mail_status = send_mail(
            subject=f'Статус Вашего бронирования изменён.',
            message=message,
            from_email='CaravelHotel.ua',
            recipient_list=[cleaned_reservation['user']['email']],
            fail_silently=True
        )
        mail_status += 1

        reservation_id = cleaned_reservation['id']
        connection.cursor().execute('insert into rooms_notification(message, status_id, request_reservation_id) values (%s, %s, %s);', [message, mail_status, reservation_id])

        return redirect('show_reservations')
    else:
        return render(request, 'change_status.html', context)


def payment(request):
    if request.user.is_anonymous or request.user.count_bookings_waiting_for_payment() == 0:
        return redirect('index')
    context = {}
    if request.method == 'POST':
        if request.FILES['receipt']:
            loaded_file = request.FILES['receipt']
            fs = FileSystemStorage(MEDIA_ROOT + '/receipts/')
            filename = fs.save(loaded_file.name, loaded_file)
            file_location = 'receipts/' + filename
            reservation_id = int(request.POST['book'])
            cursor = connection.cursor()
            cursor.execute('insert into rooms_receipt(reservation_id, receipt) values(%s, %s);',
                           [reservation_id, file_location])
            cursor.execute('update rooms_RequestReservation set status_id = 3 where id = %s', [reservation_id])
            context['receipt_message'] = True
        return show_profile(request, request.user.login, context)
    else:
        bookings = []
        raw_bookings = request.user.get_user_bookings_raw_dict()
        cleaned_bookings = request.user.get_user_bookings()
        for i in range(len(raw_bookings)):
            if raw_bookings[i]['status_id'] != 2:
                continue
            temp_dict = {}
            temp_dict['id'] = raw_bookings[i]['id']
            temp_dict[
                'name'] = f'{cleaned_bookings[i]["room"]}, {cleaned_bookings[i]["arrival_date"]}, {cleaned_bookings[i]["departure_date"]}'
            bookings.append(temp_dict)

        context = {
            'bookings': bookings
        }
        return render(request, 'payment.html', context)


def token_payment(request, token):
    context = {
        'token': token,
        'reservation': {},
        'customer': {},
    }
    reservation = RequestReservation.get_reservation_by_token(token)
    if not reservation or reservation['status_id'] != 2:
        redirect('index')

    context['reservation']['room'] = Room.get_name_by_id(reservation['room_id'])
    context['reservation']['arrival_date'] = reservation['arrival_date']
    context['reservation']['departure_date'] = reservation['departure_date']
    customer = None
    if reservation['user_id']:
        customer = User.get_user_description_by_id(reservation['user_id'])
    else:
        customer = Guest.get_guest_description_by_id(reservation['guest_id'])

    context['customer']['name'] = customer['name']
    context['customer']['surname'] = customer['surname']
    context['customer']['email'] = customer['email']
    context['customer']['phone_number'] = customer['phone_number']

    if request.method == 'POST':
        if request.FILES['receipt']:
            loaded_file = request.FILES['receipt']
            fs = FileSystemStorage(MEDIA_ROOT + '/receipts/')
            filename = fs.save(loaded_file.name, loaded_file)
            file_location = 'receipts/' + filename
            cursor = connection.cursor()
            cursor.execute('insert into rooms_receipt(reservation_id, receipt) values(%s, %s);', [reservation['id'], file_location])
            cursor.execute('update rooms_RequestReservation set status_id = 3 where id = %s', [reservation['id']])
            context['receipt_message'] = True
        return thanks_receipt(request)

    print(context)
    return render(request, 'payment.html', context)


def thanks_receipt(request):
    return render(request, 'thanks_receipt.html')
