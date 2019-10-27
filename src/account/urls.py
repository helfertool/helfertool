from django.conf.urls import url

from . import views

app_name = 'account'
urlpatterns = [
    # account
    url(r'^$',
        views.view_user,
        name='view_user'),

    url(r'^(?P<user_pk>[0-9]+)/$',
        views.view_user,
        name='view_user'),

    url(r'^(?P<user_pk>[0-9]+)/edit/$',
        views.edit_user,
        name='edit_user'),

    url(r'^new/$',
        views.add_user,
        name='add_user'),

    url(r'^list/$',
        views.list_users,
        name='list_users'),

    # agreements
    url(r'^check/$',
        views.check_user_agreement,
        name='check_user_agreement'),

    url(r'^check/(?P<agreement_pk>[0-9]+)/$',
        views.handle_user_agreement,
        name='handle_user_agreement'),

    url(r'^agreements/$',
        views.list_agreements,
        name='list_agreements'),

    url(r'^agreements/new/$',
        views.edit_agreement,
        name='new_agreement'),

    url(r'^agreements/(?P<agreement_pk>[0-9]+)/$',
        views.edit_agreement,
        name='edit_agreement'),

    url(r'^agreements/(?P<agreement_pk>[0-9]+)/delete/$',
        views.delete_agreement,
        name='delete_agreement'),
]
