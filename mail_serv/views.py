import smtplib
import threading
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from config.settings import EMAIL_HOST_USER
from mail_serv.forms import MailingForm, MessageManagementForm, RecipientForm
from mail_serv.models import EmailSendingAttempt, Mailing, MessageManagement, Recipient
from mail_serv.services import (
    get_mailings_from_cache,
    get_messages_from_cache,
    get_recipients_from_cache,
)


def home(request):
    """Представление для отображения домашней страницы."""
    return render(request, "mail_serv/home.html")


class RecipientView(ListView):
    """Представление для отображения списка получателей."""

    model = Recipient
    template_name = "mail_serv/profile.html"
    context_object_name = "recipients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_perm("mail_serv.can_disable_mailing"):
            context["mailings"] = Mailing.objects.all()
            context["recipients"] = Recipient.objects.all()
            context["messagemanagements"] = MessageManagement.objects.all()
            context["total_messages"] = MessageManagement.objects.count()
            context["total_recipients"] = Recipient.objects.count()
            context["total_mailings"] = Mailing.objects.count()
        else:
            context["mailings"] = Mailing.objects.filter(owner=self.request.user)
            context["recipients"] = Recipient.objects.filter(owner=self.request.user)
            context["messagemanagements"] = MessageManagement.objects.filter(
                owner=self.request.user
            )
            context["total_messages"] = MessageManagement.objects.filter(
                owner=self.request.user
            ).count()
            context["total_recipients"] = Recipient.objects.filter(
                owner=self.request.user
            ).count()
            context["total_mailings"] = Mailing.objects.filter(
                owner=self.request.user
            ).count()
        return context

    def get_queryset(self):
        """'Получение списка получателей из кэша."""
        recipients = get_recipients_from_cache()
        messages = get_messages_from_cache()
        mailings = get_mailings_from_cache()
        return recipients, messages, mailings


class RecipientCreateView(CreateView, LoginRequiredMixin):
    """Представление для создания получателя."""

    model = Recipient
    form_class = RecipientForm

    def get_success_url(self):
        """Получение адреса для перенаправления после создания."""
        return reverse_lazy("mail_serv:profile")

    def form_valid(self, form):
        """'Создание получателя."""
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(UpdateView, LoginRequiredMixin):
    """Представление для обновления получателя."""

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mail_serv:profile")


class RecipientDeleteView(DeleteView, LoginRequiredMixin):
    """Представление для удаления получателя."""

    model = Recipient

    def get_success_url(self):
        """Получение адреса для перенаправления после удаления."""
        return reverse_lazy("mail_serv:profile")

    def delete(self, request, *args, **kwargs):
        """'Удаление получателя."""
        self.object = self.get_object()
        if request.method == "POST":
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.get(self.request, *args, **kwargs)


class RecipientDetailView(DetailView, LoginRequiredMixin):
    """'Представление для получателя."""

    model = Recipient
    template_name = "mail_serv/recipient_detail.html"
    context_object_name = "recipient"


class MessageManagementCreateView(CreateView, LoginRequiredMixin):
    """'Представление для создания сообщения."""

    model = MessageManagement
    form_class = MessageManagementForm
    success_url = reverse_lazy("mail_serv:profile")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageManagementUpdateView(UpdateView, LoginRequiredMixin):
    """'Представление для обновления сообщения."""

    model = MessageManagement
    form_class = MessageManagementForm

    def get_success_url(self):
        return reverse_lazy("mail_serv:profile")


class MessageManagementDeleteView(DeleteView, LoginRequiredMixin):
    """Представление для удаления сообщения."""

    model = MessageManagement
    success_url = reverse_lazy("mail_serv:profile")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.method == "POST":
            self.object.delete()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.get(self.request, *args, **kwargs)


class MessageManagementDetailView(DetailView, LoginRequiredMixin):
    """'Представление для сообщения."""

    model = MessageManagement
    template_name = "mail_serv/message_detail.html"
    context_object_name = "messagemanagement"


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания рассылки."""

    model = Mailing
    form_class = MailingForm
    template_name = "mail_serv/mailing_form.html"
    success_url = reverse_lazy("mail_serv:profile")

    def get_form_kwargs(self):
        """Получает дополнительные аргументы для формы и добавляет текущего пользователя в них."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """'Создание рассылки."""
        form.instance.owner = self.request.user
        mailing = form.save(commit=False)
        mailing.status = "Создана"
        mailing.save()
        return super().form_valid(form)


class MailingDetailView(DetailView, LoginRequiredMixin):
    """Представление для рассылки."""

    model = Mailing
    template_name = "mail_serv/mailing_detail.html"
    context_object_name = "mailing"


class MailingDeleteView(DeleteView, LoginRequiredMixin):
    """Представление для удаления рассылки."""

    model = Mailing
    success_url = reverse_lazy("mail_serv:profile")


class MailingUpdateView(UpdateView, LoginRequiredMixin):
    """Представление для обновления рассылки."""

    model = Mailing
    form_class = MailingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("mail_serv:profile")


class MailingSendView(View, LoginRequiredMixin):
    """Представление для отправки рассылки."""

    def post(self, request, pk=None):
        if pk is None:
            pk = request.POST.get("pk")
        mailing = Mailing.objects.get(id=pk)
        mailing.status = "Запущена"
        mailing.save()
        owner = self.request.user
        thread = threading.Thread(target=send_message, args=(mailing.id, owner))
        thread.start()
        return HttpResponseRedirect(reverse_lazy("mail_serv:profile"))


def send_message(mailing_id, owner):
    """'Функция для отправки рассылки."""
    mailing = Mailing.objects.get(id=mailing_id)
    mailing.status = "Запущена"
    mailing.save()
    mailing = Mailing.objects.get(id=mailing_id)
    recipients = mailing.recipients.all()
    end = mailing.ended_at
    current_time = timezone.now()
    if current_time > end:
        mailing.status = "Завершена"
        mailing.save()
        return

    while timezone.now() < end:
        mailing.refresh_from_db()
        if mailing.status == "Завершена":
            break
        else:
            for recipient in recipients:
                try:
                    send_mail(
                        mailing.message.subject,
                        mailing.message.body,
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    EmailSendingAttempt.objects.create(
                        status="Успешно",
                        server_response="Сообщение отправлено",
                        mailing=mailing,
                        owner=owner,
                    )
                except smtplib.SMTPRecipientsRefused as e:
                    print(
                        f"Ошибка при отправке письма, проверьте правильность написания почты: {e}"
                    )
                    EmailSendingAttempt.objects.create(
                        status="Не успешно",
                        server_response="Почты не существует",
                        mailing=mailing,
                        owner=owner,
                    )
                except Exception as e:
                    print(f"Ошибка при отправке письма: {e}")
                    EmailSendingAttempt.objects.create(
                        status="Не успешно",
                        server_response=f"Ошибка при отправке {e}",
                        mailing=mailing,
                        owner=owner,
                    )
            time.sleep(30)

            mailing.status = "Завершена"
            mailing.save()


@method_decorator(cache_page(60 * 15), name="dispatch")
class EmailSendingAttemptListView(ListView, LoginRequiredMixin):
    """Представление для списка попыток отправки."""

    model = EmailSendingAttempt
    context_object_name = "emailsendingattempts"

    def get_template_names(self):
        if self.request.path == "/mail_serv/statistic/":
            return ["mail_serv/statistic.html"]
        else:
            return ["mail_serv/emailsending_list.html"]

    def get_queryset(self):
        mailing_id = self.request.GET.get("mailing_id")
        user = self.request.user

        if mailing_id:
            queryset = EmailSendingAttempt.objects.filter(
                mailing_id=mailing_id, owner=user
            )
        else:
            queryset = EmailSendingAttempt.objects.filter(owner=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["successful_attempts_count"] = self.object_list.filter(
            status="Успешно"
        ).count()
        context["unsuccessful_attempts_count"] = self.object_list.filter(
            status="Не успешно"
        ).count()
        context["successful_emailsendingattempts"] = self.object_list.filter(
            status="Успешно"
        )
        context["unsuccessful_emailsendingattempts"] = self.object_list.filter(
            status="Не успешно"
        )
        return context


class DisableMailingView(LoginRequiredMixin, View):
    """Представление для отмены рассылки."""

    def post(self, request, **kwargs):
        mailing_id = kwargs.get("mailing_id")
        if not mailing_id:
            return HttpResponseBadRequest("Не передан ID рассылки")

        mailing = get_object_or_404(Mailing, pk=mailing_id)

        if not request.user.has_perm("mail_serv.can_disable_mailing"):
            return HttpResponseForbidden("Недостаточно прав")

        mailing.status = "Завершена"
        mailing.save()
        return redirect("mail_serv:profile")
