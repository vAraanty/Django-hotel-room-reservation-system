from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.db import connection

from caravel.utils import dictfetchall
from rooms.models import User, Guest, Room


def cron_job():
    current_date = datetime.now().date() + timedelta(days=3)
    cursor = connection.cursor()
    raw_dict = dictfetchall(cursor.execute('select id, arrival_date, user_id, guest_id, room_id from rooms_requestreservation where arrival_date = %s and status_id = 2', [current_date]))
    for reservation in raw_dict:
        cursor.execute('update rooms_requestreservation set status_id = 5 where id = %s', [reservation['id']])

        user_information = {}
        if reservation['user_id']:
            user_information = User.get_user_description_by_id(reservation['user_id'])
        else:
            user_information = Guest.get_guest_description_by_id(reservation['guest_id'])

        message = f'Приветствуем, {user_information["name"]}.\n\n'
        message += f'Статус Вашего бронирования {Room.get_name_by_id(reservation["room_id"])} номера, на дату въезда {reservation["arrival_date"]} был отклонён, так как оплата по бронированию предоставлена не была.'
        mail_status = send_mail(
            subject=f'Данные профиля изменены!',
            message=message,
            from_email='CaravelHotel.ua',
            recipient_list=[user_information['email']],
            fail_silently=True
            )
        mail_status += 1

        if reservation['user_id']:
            cursor.execute('insert into rooms_notification(message, status_id, user_id) values (%s, %s, %s);', [message, mail_status, reservation['user_id']])
        else:
            cursor.execute('insert into rooms_notification(message, status_id, user_id) values (%s, %s, %S);', [message, mail_status, reservation['guest_id']])
