from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm

from mail_serv.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    '''Форма регистрации пользователя'''
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class CustomSetPasswordForm(StyleFormMixin, SetPasswordForm):
    '''Форма смены пароля'''
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=True,
        help_text="Пароль должен содержать как минимум 8 символов.",
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        required=True,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Введите тот же пароль, что и выше.",
    )
