from django.conf.urls import url

from . import views

app_name = 'importexport'
urlpatterns = [
    # export for import
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/import/job/$',
        views.import_job_template,
        name='import_job_template'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/job/(?P<job_pk>[0-9]+)/$',
        views.export_job_template,
        name='export_job_template'),


    # helper export
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/all/$',
        views.export,
        name='export_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/all/'
        r'(?P<date_str>\d{4}-\d{2}-\d{2})/$',
        views.export,
        name='export_date'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/'
        r'(?P<job_pk>[0-9]+)/$',
        views.export,
        name='export_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/'
        r'(?P<job_pk>[0-9]+)/(?P<date_str>\d{4}-\d{2}-\d{2})/$',
        views.export,
        name='export_job_date'),
]
