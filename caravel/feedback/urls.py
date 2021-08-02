from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='feedback_index'),
    path('feedbacks/', show_feedbacks, name='show_feedbacks'),
]