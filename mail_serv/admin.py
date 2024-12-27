from django.contrib import admin

from mail_serv.models import Mailing, MessageManagement, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Представление администратора для модели Recipient."""

    list_display = ("id", "initials", "email")


@admin.register(MessageManagement)
class MessageManagementAdmin(admin.ModelAdmin):
    """Представление администратора для модели MessageManagement."""

    list_display = ("id", "subject")
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Представление администратора для модели Mailing."""

    list_display = ("id", "message", "status")
    list_filter = ("status",)
    search_fields = ("message_management__subject", "recipient__initials")
