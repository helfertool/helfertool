from django.urls import path

from . import views

app_name = "corona"
urlpatterns = [
    path("<slug:event_url_name>/corona/settings/", views.settings, name="settings"),
    path("<slug:event_url_name>/corona/cleanup/", views.cleanup, name="cleanup"),
    path("<slug:event_url_name>/corona/data/", views.data, name="data"),
    path("<slug:event_url_name>/corona/export/", views.export, name="export"),
    path("<slug:event_url_name>/corona/missing/", views.missing, name="missing"),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/corona/",
        views.view_helper,
        name="view_helper",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/corona/edit/",
        views.edit_helper,
        name="edit_helper",
    ),
]
