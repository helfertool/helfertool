from django.conf.urls import url

from . import views


app_name = 'toollog'
urlpatterns = [
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/auditlog/$',
        views.event_audit_log,
        name='event_audit_log'),
]
