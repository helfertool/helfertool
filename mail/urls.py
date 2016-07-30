from django.conf.urls import url

from . import views

app_name = 'mail'
urlpatterns = [
    # send mails
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/mail/$',
        views.send_mail,
        name='send_mail'),
]
