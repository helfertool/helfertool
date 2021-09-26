from django.conf.urls import url

from . import views

app_name = 'corona'
urlpatterns = [
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/corona/settings/$',
        views.settings,
        name='settings'),
]
