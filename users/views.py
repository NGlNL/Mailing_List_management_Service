import secrets

from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, View

from config.settings import EMAIL_HOST_USER
from users.forms import CustomSetPasswordForm, UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    '''Представление для создания нового пользователя.'''
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}"
        send_mail(
            subject="Подтверждение регистрации",
            message=f"Подтвердите регистрацию на {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        group_name = "Пользователь"
        group, created = Group.objects.get_or_create(name=group_name)
        group.user_set.add(user)

        return super().form_valid(form)


def email_verification(request, token):
    '''Функция для подтверждения email пользователя.'''
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class PasswordResetRequestView(View):
    '''Представление для запроса сброса пароля пользователя.'''
    template_name = "users/password_reset_form.html"
    success_url = "users:login"

    def get(self, request):
        '''Функция для получения формы сброса пароля.'''
        token = request.GET.get("token")
        if token:
            user = get_object_or_404(User, token=token)
            if user:
                form = CustomSetPasswordForm(user)
                return render(request, self.template_name, {"form": form})
            else:
                return HttpResponse("Invalid token")
        else:
            form = PasswordResetForm()
            return render(request, self.template_name, {"form": form})

    def post(self, request):
        '''Функция для отправки запроса на сброс пароля.'''
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, email=form.cleaned_data["email"])
            if user:
                token = secrets.token_hex(16)
                user.token = token
                user.save()
                host = request.get_host()
                url = f"http://{host}/users/password_reset_confirm/{token}/"
                send_mail(
                    subject="Подтверждение сброса пароля",
                    message=f"Нажмите на ссылку для сброса пароля: {url}",
                    from_email="ng_nl01@mail.ru",
                    recipient_list=[user.email],
                )
                return redirect("users:login")
        return render(request, self.template_name, {"form": form})


class PasswordResetConfirmView(View):
    '''Представление для подтверждения сброса пароля пользователя.'''
    template_name = "users/password_reset_confirm.html"
    form_class = CustomSetPasswordForm

    def get(self, request, token):
        user = get_object_or_404(User, token=token)
        if not default_token_generator.check_token(user, token):
            return render(request, self.template_name, {"error": "Истекший токен"})
        else:
            form = self.form_class(initial={"email": user.email})
            return render(request, self.template_name, {"form": form})

    def post(self, request, token):
        '''Функция для подтверждения сброса пароля пользователя.'''
        user = get_object_or_404(User, token=token)
        if request.method == "POST":
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                login(request, user)
                return redirect("users:login")
        else:
            form = CustomSetPasswordForm(user)
        context = {
            "form": form,
        }
        return render(request, "users/password_reset_confirm.html", context)


class UserListView(ListView):
    '''Представление для отображения списка пользователей.'''
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        '''Функция для получения списка пользователей с сортировкой.'''
        return User.objects.all().order_by("id")


class BlockUserView(LoginRequiredMixin, PermissionRequiredMixin, View):
    '''Представление для блокировки пользователя.'''
    permission_required = "users.can_block_service_users"

    def post(self, request, **kwargs):
        '''Функция для блокировки пользователя.'''
        user_id = kwargs.get("user_id")
        if not user_id:
            return HttpResponseBadRequest("Не передан ID пользователя")

        user_to_block = get_object_or_404(User, pk=user_id)

        if user_to_block.id == request.user.id:
            return HttpResponseBadRequest("Нельзя заблокировать самого себя")

        user_to_block.is_active = False
        user_to_block.save()

        return redirect("users:user_list")


class UnblockUserView(LoginRequiredMixin, PermissionRequiredMixin, View):
    '''Представление для разблокировки пользователя.'''
    permission_required = "users.can_block_service_users"

    def post(self, request, **kwargs):
        '''Функция для разблокировки пользователя.'''
        user_id = kwargs.get("user_id")
        if not user_id:
            return HttpResponseBadRequest("Не передан ID пользователя")

        user_to_unblock = get_object_or_404(User, pk=user_id)

        if user_to_unblock.id == request.user.id:
            return HttpResponseBadRequest("Нельзя разблокировать самого себя")

        user_to_unblock.is_active = True
        user_to_unblock.save()

        return redirect("users:user_list")
