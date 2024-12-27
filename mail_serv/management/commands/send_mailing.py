import smtplib

from django.core.mail import send_mail
from django.core.management import BaseCommand

from mail_serv.models import Mailing


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **kwargs):
        mailing_id = kwargs["mailing_id"]
        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR("Mailing not found"))
        mailing.status = "Отправлено"
        mailing.save()
        recipients = mailing.recipients.all()
        for recipient in recipients:
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    "ng_nl01@mail.ru",
                    [recipient.email],
                    fail_silently=False,
                )
            except smtplib.SMTPRecipientsRefused as e:
                print(
                    f"Ошибка при отправке письма, проверьте правильность написания почты: {e}"
                )
        mailing.status = "Завершена"
        mailing.save()
        self.stdout.write(self.style.SUCCESS("Письмо отправлено"))
