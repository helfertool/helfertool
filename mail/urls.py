from django.conf.urls import url

from . import views

app_name = 'mail'
urlpatterns = [
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/mail/$',
        views.send_mail,
        name='send'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/mail/list/$',
        views.list_mails,
        name='list'),
]
