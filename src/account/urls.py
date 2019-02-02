from django.conf.urls import url

from . import views

app_name = 'account'
urlpatterns = [
    # account
    url(r'^$',
        views.change_user,
        name='change_user'),

    # agreements
    url(r'^agreements/$',
        views.check_user_agreement,
        name='check_user_agreement'),

    url(r'^agreements/(?P<agreement_pk>[0-9]+)/$',
        views.handle_user_agreement,
        name='handle_user_agreement'),
]
