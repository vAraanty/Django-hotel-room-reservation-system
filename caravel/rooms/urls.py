from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='rooms_index'),
    path('<int:room_id>', show_room, name='show_room'),
    path('task/task/', task)
]