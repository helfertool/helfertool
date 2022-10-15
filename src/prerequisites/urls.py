from django.urls import path

from . import views

app_name = "prerequisites"
urlpatterns = [
    path("<slug:event_url_name>/prerequisites/", views.view_prerequisites, name="view_prerequisites"),
    path("<slug:event_url_name>/prerequisites/new/", views.edit_prerequisite, name="new_prerequisite"),
    path(
        "<slug:event_url_name>/prerequisites/<int:prerequisite_pk>/edit/",
        views.edit_prerequisite,
        name="edit_prerequisite",
    ),
    path(
        "<slug:event_url_name>/prerequisites/<int:prerequisite_pk>/delete/",
        views.delete_prerequisite,
        name="delete_prerequisite",
    ),
    path(
        "<slug:event_url_name>/prerequisites/<int:prerequisite_pk>/helpers/",
        views.view_helpers_prerequisite,
        name="view_helpers_prerequisite",
    ),
]
