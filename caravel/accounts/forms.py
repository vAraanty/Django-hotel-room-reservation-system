from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import widgets


class SignUpForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ('name', 'surname', 'email', 'login', 'phone_number', 'password1', 'password2')

