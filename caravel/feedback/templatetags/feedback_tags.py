from django import template
from django.db import connection

from caravel.utils import dictfetchall
from feedback.models import Feedback
from rooms.models import User, Room

register = template.Library()


@register.simple_tag()
def get_feedbacks():
    feedbacks = dictfetchall(connection.cursor().execute('select * from feedback_feedback'))
    cleaned_feedbacks = []
    for feedback in feedbacks:
        cleaned_feedback = {}
        user_description = User.get_user_description_by_id(feedback['user_id'])
        cleaned_feedback['user'] = user_description['name'] + ' ' + user_description['surname']
        cleaned_feedback['room'] = Room.get_name_by_id(feedback['room_id'])
        cleaned_feedback['rating'] = feedback['rating']
        cleaned_feedback['when_given'] = feedback['when_given']
        cleaned_feedback['content'] = feedback['content']
        cleaned_feedbacks.append(cleaned_feedback)

    return cleaned_feedbacks


@register.filter()
def create_range(value, start_index=0):
    return range(start_index, value+start_index)
