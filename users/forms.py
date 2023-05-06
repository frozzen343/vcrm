from django.contrib.auth.forms import UserCreationForm
# from django import forms

from users.models import User


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
