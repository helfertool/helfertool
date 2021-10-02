from django.conf.urls import url

from . import views

app_name = 'corona'
urlpatterns = [
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/corona/settings/$',
        views.settings,
        name='settings'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/corona/cleanup/$',
        views.cleanup,
        name='cleanup'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/corona/data/$',
        views.data,
        name='data'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/corona/export/$',
        views.export,
        name='export'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/corona/missing/$',
        views.missing,
        name='missing'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/(?P<helper_pk>[0-9a-f\-]+)/corona/$',
        views.view_helper,
        name='view_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/(?P<helper_pk>[0-9a-f\-]+)/corona/edit/$',
        views.edit_helper,
        name='edit_helper'),
]
