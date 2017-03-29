from django.conf.urls import url

from . import views

app_name = 'inventory'
urlpatterns = [
    # event
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/register/$',
        views.register_item,
        name='register'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/register/(?P<item_pk>[0-9]+)/$',
        views.register_badge,
        name='register_badge'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/take_back/$',
        views.take_back_item,
        name='take_back'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/take_back/(?P<item_pk>[0-9]+)/$',
        views.take_back_badge,
        name='take_back_badge'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/take_back/(?P<item_pk>[0-9]+)/direct/$',
        views.take_back_direct,
        name='take_back_direct'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/list/$',
        views.event_list,
        name='list'),

    # admin
    url(r'^admin/inventory/$',
        views.inventory_list,
        name='inventory_list'),
]
