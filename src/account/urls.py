from django.conf import settings
from django.conf.urls import url

from . import views

app_name = 'account'
urlpatterns = [
    # account
    url(r'^$',
        views.change_user,
        name='change_user'),

    url(r'^new/$',
        views.add_user,
        name='add_user'),

    # permissions
    url(r'^permissions/$',
        views.permissions,
        name='permissions'),

    url(r'^permissions/(?P<user_pk>[0-9]+)/user/delete/$',
        views.delete_permission, {'groupname': settings.GROUP_ADDUSER},
        name='delete_user_permission'),

    url(r'^permissions/(?P<user_pk>[0-9]+)/event/delete/$',
        views.delete_permission, {'groupname': settings.GROUP_ADDEVENT},
        name='delete_event_permission'),

    url(r'^permissions/(?P<user_pk>[0-9]+)/news/delete/$',
        views.delete_permission, {'groupname': settings.GROUP_SENDNEWS},
        name='delete_news_permission'),

    # agreements
    url(r'^agreements/$',
        views.check_user_agreement,
        name='check_user_agreement'),

    url(r'^agreements/(?P<agreement_pk>[0-9]+)/$',
        views.handle_user_agreement,
        name='handle_user_agreement'),
]
