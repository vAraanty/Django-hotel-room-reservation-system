from django.urls import path

from .views import show_profile, login_user, sign_up, change_info

urlpatterns = [
    path('signup/', sign_up, name='signup'),
    path('login/', login_user, name='login'),
    path('user/<str:user_login>', show_profile, name='show_profile'),
    path('user/<str:user_login>/change_info/', change_info, name='change_info'),
]
