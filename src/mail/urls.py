from django.urls import path

from . import views

app_name = "mail"
urlpatterns = [
    path("<slug:event_url_name>/mail/", views.send_mail, name="send"),
    path("<slug:event_url_name>/mail/list/", views.list_mails, name="list"),
    path("<slug:event_url_name>/mail/<int:mail_pk>/", views.show_mail, name="show"),
    path(
        "<slug:event_url_name>/mail/<int:mail_pk>/errors/",
        views.show_mail_errors,
        name="show_errors",
    ),
]
