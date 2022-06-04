from django.conf.urls import url

from . import views

app_name = "prerequisites"
urlpatterns = [
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/prerequisites/$", views.view_prerequisites, name="view_prerequisites"),
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/prerequisites/new/$", views.edit_prerequisite, name="new_prerequisite"),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/prerequisites/(?P<prerequisite_pk>[0-9]+)/edit/$",
        views.edit_prerequisite,
        name="edit_prerequisite",
    ),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/prerequisites/(?P<prerequisite_pk>[0-9]+)/delete/$",
        views.delete_prerequisite,
        name="delete_prerequisite",
    ),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/prerequisites/(?P<prerequisite_pk>[0-9]+)/helpers/$",
        views.view_helpers_prerequisite,
        name="view_helpers_prerequisite",
    ),
]
