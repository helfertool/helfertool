from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = "account"
urlpatterns = [
    # password reset
    path(
        "reset/",
        auth_views.PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            template_name="account/password_reset/form.html",
            success_url=reverse_lazy("account:password_reset_sent"),
            email_template_name="account/password_reset/confirm_mail.txt",
            subject_template_name="account/password_reset/confirm_mail_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "reset/sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="account/password_reset/sent.html",
        ),
        name="password_reset_sent",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=CustomSetPasswordForm,
            template_name="account/password_reset/confirm.html",
            success_url=reverse_lazy("account:password_reset_completed"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/completed/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="account/password_reset/completed.html",
        ),
        name="password_reset_completed",
    ),
    # account
    path("", views.view_user, name="view_user"),
    path("<int:user_pk>/", views.view_user, name="view_user"),
    path("<int:user_pk>/edit/", views.edit_user, name="edit_user"),
    path("<int:user_pk>/delete/", views.delete_user, name="delete_user"),
    path("<int:user_pk>/merge/", views.merge_user, name="merge_user"),
    path("new/", views.add_user, name="add_user"),
    path("list/", views.list_users, name="list_users"),
    # agreements
    path("check/", views.check_user_agreement, name="check_user_agreement"),
    path("check/<int:agreement_pk>/", views.handle_user_agreement, name="handle_user_agreement"),
    path("agreements/", views.list_agreements, name="list_agreements"),
    path("agreements/new/", views.edit_agreement, name="new_agreement"),
    path("agreements/<int:agreement_pk>/", views.edit_agreement, name="edit_agreement"),
    path("agreements/<int:agreement_pk>/delete/", views.delete_agreement, name="delete_agreement"),
]
