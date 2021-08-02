from django.contrib import admin

# Register your models here.
from .models import *


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'room', 'content', 'when_given')
    search_fields = ('user', 'content')
    list_filter = ('room', 'rating')


admin.site.register(Feedback, FeedbackAdmin)
