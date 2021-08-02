from django import template
from django.db import connection

from rooms.models import Room

register = template.Library()


@register.simple_tag()
def get_rooms():
    return Room.objects.raw('SELECT * FROM rooms_room')
