from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from caravel.utils import dictfetchall


def index(request):
    rooms = dictfetchall(connection.cursor().execute('select id, name from rooms_room;'))
    context = {
        'rooms': rooms,
    }
    if request.method == 'GET':
        return render(request, 'feedback/index.html', context)
    else:
        if request.user.is_anonymous:
            return render(request, 'feedback/index.html', context)
        errors = {}
        room = request.POST['room']
        if not room:
            errors['room'] = True
        rating = request.POST['rating']
        if not rating:
            errors['rating'] = True
        content = request.POST['content']
        if not content:
            errors['content'] = True

        context['errors'] = errors
        if len(errors):
            return render(request, 'feedback/index.html', context)

        connection.cursor().execute('insert into feedback_feedback(user_id, rating, room_id, content, when_given) values (%s, %s, %s, %s, datetime(\'now\'));', [request.user.pk, rating, room, content])
        return redirect(show_feedbacks)


def show_feedbacks(request):
    context = {
        'title': 'Пользовательские отзывы'
    }
    return render(request, 'feedback/show_feedbacks.html', context)
