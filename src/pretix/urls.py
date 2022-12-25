from django.conf.urls import url

from . import views

app_name = "pretix"
urlpatterns = [
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/pretix/settings/$", views.settings, name="settings"),
]
