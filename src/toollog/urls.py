from django.urls import path

from . import views


app_name = "toollog"
urlpatterns = [
    path("<slug:event_url_name>/auditlog/", views.event_audit_log, name="event_audit_log"),
]
