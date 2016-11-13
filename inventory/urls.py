from django.conf.urls import url

from . import views

app_name = 'inventory'
urlpatterns = [
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/register/$',
        views.register_item,
        name='register'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/register/badge/$',
        views.register_badge,
        name='register_badge'),
]
