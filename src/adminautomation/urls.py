from django.urls import path

from . import views

app_name = "adminautomation"
urlpatterns = [
    path("manage/archivestatus/", views.event_archive_status, name="event_archive_status"),
    path(
        "<slug:event_url_name>/archiveexception/",
        views.edit_event_archive_exception,
        name="edit_event_archive_exception",
    ),
]
