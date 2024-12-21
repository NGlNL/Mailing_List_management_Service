from django.conf import settings
from django.db import models


class Recipient(models.Model):
    '''Модель получателя'''
    email = models.CharField(max_length=100, unique=False)
    initials = models.CharField(max_length=100, verbose_name="Ф.И.О.")
    comment = models.TextField(max_length=150, verbose_name="Комментарий")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

    def __str__(self):
        return self.initials


class MessageManagement(models.Model):
    '''Модель сообщений'''
    subject = models.CharField(max_length=100, verbose_name="Тема письма")
    body = models.TextField(max_length=1000, verbose_name="Тело письма")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    '''Модель рассылок'''
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    started_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата запуска"
    )
    ended_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата завершения"
    )
    status = models.CharField(
        max_length=10,
        choices=(
            ("Created", "Создана"),
            ("Started", "Запущена"),
            ("Finished", "Завершена"),
        ),
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        MessageManagement, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(Recipient, verbose_name="Получатели")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [("can_disable_mailing", "Can disable mailing")]

    def __str__(self):
        return f"Рассылка {self.message}"


class EmailSendingAttempt(models.Model):
    '''Модель попыток отправки'''
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=[("Успешно", "Успешно"), ("Не успешно", "Не успешно")]
    )
    server_response = models.TextField()
    mailing = models.ForeignKey("Mailing", on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )

    objects = models.Manager()

    def __str__(self):
        return f"Попытка рассылки {self.datetime}"
