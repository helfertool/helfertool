from django.conf.urls import url

from . import views

app_name = "mail"
urlpatterns = [
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/mail/$", views.send_mail, name="send"),
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/mail/list/$", views.list_mails, name="list"),
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/mail/(?P<mail_pk>[0-9]+)/$", views.show_mail, name="show"),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/mail/(?P<mail_pk>[0-9]+)/errors/$",
        views.show_mail_errors,
        name="show_errors",
    ),
]
