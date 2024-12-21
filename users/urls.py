from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import (BlockUserView, PasswordResetConfirmView,
                         PasswordResetRequestView, UnblockUserView,
                         UserCreateView, UserListView, email_verification)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("password_reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password_reset_confirm/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("users/block/<int:user_id>/", BlockUserView.as_view(), name="block_user"),
    path(
        "users/unblock/<int:user_id>/", UnblockUserView.as_view(), name="unblock_user"
    ),
]
