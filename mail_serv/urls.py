from django.urls import path
from django.views.decorators.cache import cache_page

from mail_serv.views import (DisableMailingView, EmailSendingAttemptListView,
                             MailingCreateView, MailingDeleteView,
                             MailingDetailView, MailingSendView,
                             MailingUpdateView, MessageManagementCreateView,
                             MessageManagementDeleteView,
                             MessageManagementDetailView,
                             MessageManagementUpdateView, RecipientCreateView,
                             RecipientDeleteView, RecipientDetailView,
                             RecipientUpdateView, RecipientView, home)

app_name = "mail_serv"

urlpatterns = [
    path("", home, name="home"),
    path("profile/", RecipientView.as_view(), name="profile"),
    path("mail_serv/create/", RecipientCreateView.as_view(), name="rec_create"),
    path("mail_serv/update/<int:pk>", RecipientUpdateView.as_view(), name="rec_update"),
    path("mail_serv/delete/<int:pk>", RecipientDeleteView.as_view(), name="rec_delete"),
    path(
        "mail_serv/detail/<int:pk>",
        cache_page(60)(RecipientDetailView.as_view()),
        name="rec_detail",
    ),
    path(
        "mail_serv/man_create/",
        MessageManagementCreateView.as_view(),
        name="management_create",
    ),
    path(
        "mail_serv/man_update/<int:pk>",
        MessageManagementUpdateView.as_view(),
        name="management_update",
    ),
    path(
        "mail_serv/man_delete/<int:pk>",
        MessageManagementDeleteView.as_view(),
        name="management_delete",
    ),
    path(
        "mail_serv/man_detail/<int:pk>",
        cache_page(60)(MessageManagementDetailView.as_view()),
        name="management_detail",
    ),
    path("mail_serv/mail_create/", MailingCreateView.as_view(), name="mail_create"),
    path(
        "mail_serv/mail_detail/<int:pk>",
        cache_page(60)(MailingDetailView.as_view()),
        name="mail_detail",
    ),
    path(
        "mail_serv/mail_delete/<int:pk>",
        MailingDeleteView.as_view(),
        name="mail_delete",
    ),
    path(
        "mail_serv/mail_update/<int:pk>",
        MailingUpdateView.as_view(),
        name="mail_update",
    ),
    path(
        "mail_serv/send_message/<int:pk>",
        MailingSendView.as_view(),
        name="send_message",
    ),
    path(
        "mail_serv/emailsenading_list/",
        EmailSendingAttemptListView.as_view(),
        name="emailsenading_list",
    ),
    path(
        "mail_serv/statistic/", EmailSendingAttemptListView.as_view(), name="statistic"
    ),
    path(
        "mail_serv/disabling/<int:mailing_id>",
        DisableMailingView.as_view(),
        name="disabling_mailing",
    ),
]
