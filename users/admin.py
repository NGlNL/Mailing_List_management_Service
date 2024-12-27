from django.contrib import admin

from users import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """Представление администратора для модели User."""

    list_display = ("id", "email", "is_active", "is_staff", "is_superuser")
    list_display_links = ("id",)
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    ordering = ("id",)
    readonly_fields = ("id",)
