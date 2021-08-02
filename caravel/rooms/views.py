from django.db import connection
from django.shortcuts import render
from django.http import Http404

# Create your views here
from caravel.utils import dictfetchall
from .models import Room, User, Guest, RequestReservationStatus


def index(request):
    context = {
        'title': 'Номера и апартаменты',
    }
    return render(request, 'rooms/index.html', context)


def show_room(request, room_id):
    try:
        room_item = Room.objects.raw('SELECT * FROM rooms_room WHERE id = %s', [room_id])[0]
    except:
        raise Http404("No model matches the given query.")
    context = {
        'room_item': room_item,
    }
    return render(request, 'rooms/show_room.html', context)


def task(request):
    bookings = dictfetchall(connection.cursor().execute('select * from rooms_requestreservation where arrival_date > \'2021-06-1\' and status_id = 4 order by room_id'))
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
                'name': user_description['surname'],
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
    }
    return render(request, 'rooms/task.html', context)
