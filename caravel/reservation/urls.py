from django.urls import path
from .views import *

urlpatterns = [
    path('book/', booking_index, name='booking_index'),
    path('reservations/', show_reservations, name='show_reservations'),
    path('reservations/change_status/<int:reservation_id>', change_status, name='change_status'),
    path('payment/', payment, name='payment'),
    path('payment/<str:token>', token_payment, name='token_payment'),
    path('thanks_for_receipt/', thanks_receipt, name='thanks_receipt'),
]