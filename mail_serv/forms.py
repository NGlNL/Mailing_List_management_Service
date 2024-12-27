from django import forms
from django.core.exceptions import ValidationError
from django.forms import BooleanField, ModelForm

from mail_serv.models import Mailing, MessageManagement, Recipient

FORBIDDEN_WORDS = [
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
]


class StyleFormMixin:
    """Миксин для стилизации полей форм."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["recipients"].queryset = Recipient.objects.filter(
                owner=self.user
            )
            self.fields["message"].queryset = MessageManagement.objects.filter(
                owner=self.user
            )
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label


class RecipientForm(StyleFormMixin, ModelForm):
    """Форма для модели Recipient с миксином стилизации полей."""

    class Meta:
        model = Recipient
        fields = ["email", "initials", "comment"]

    def clean_initials(self):
        initials = self.cleaned_data["initials"].lower()
        for word in FORBIDDEN_WORDS:
            if word in initials:
                raise ValidationError(f"Недопустимое слово: {word}")
        return initials


class MessageManagementForm(StyleFormMixin, ModelForm):
    """Форма для модели MessageManagement с миксином стилизации полей."""

    class Meta:
        model = MessageManagement
        fields = ["subject", "body"]

    def clean_subject(self):
        subject = self.cleaned_data["subject"].lower()
        for word in FORBIDDEN_WORDS:
            if word in subject:
                raise ValidationError(f"Недопустимое слово: {word}")
        return subject


class MailingForm(StyleFormMixin, ModelForm):
    """Форма для модели Mailing с миксином стилизации полей."""

    started_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        )
    )
    ended_at = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        )
    )

    class Meta:
        model = Mailing
        fields = ["started_at", "ended_at", "message", "recipients"]
