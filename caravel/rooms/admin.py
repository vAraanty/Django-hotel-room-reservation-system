from django.contrib import admin

# Register your models here.
from .models import *


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3
    max_num = 3


class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'price', 'exists', 'adult_capacity', 'child_capacity', 'area')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    list_editable = ('description', 'price', 'exists')
    list_filter = ('adult_capacity', 'child_capacity')
    inlines = [RoomImageInline, ]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'email', 'phone_number')
    search_fields = ('name', 'surname', 'email', 'phone_number')


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'login', 'email', 'phone_number')
    search_fields = ('name', 'surname', 'login', 'email', 'phone_number')


class RequestReservationStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name', )


class RequestReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'arrival_date', 'departure_date', 'status', 'user', 'guest')
    list_filter = ('room', 'arrival_date', 'departure_date', 'status')


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'reservation')


class NotificationStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name', )


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status', 'request_reservation')
    list_filter = ('status', 'request_reservation')
    search_fields = ('message', )


class ReservationStatusLogAdmin(admin.ModelAdmin):
    list_display = ('request_reservation', 'when_changed', 'new_status')
    list_filter = ('request_reservation', 'new_status')


admin.site.register(Room, RoomAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(RequestReservationStatus, RequestReservationStatusAdmin)
admin.site.register(RequestReservation, RequestReservationAdmin)
admin.site.register(NotificationStatus, NotificationStatusAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ReservationStatusLog, ReservationStatusLogAdmin)
admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Guest, GuestAdmin)
