from django.conf.urls import url

from . import views

app_name = "inventory"
urlpatterns = [
    # pages for single event
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/settings/$", views.event_settings, name="event_settings"),
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/register/$", views.register_item, name="register"),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/register/" "(?P<item_pk>[0-9]+)/$",
        views.register_badge,
        name="register_badge",
    ),
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/take_back/$", views.take_back_item, name="take_back"),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/take_back/" "(?P<item_pk>[0-9]+)/$",
        views.take_back_badge,
        name="take_back_badge",
    ),
    url(
        r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/take_back/" "(?P<item_pk>[0-9]+)/direct/$",
        views.take_back_direct,
        name="take_back_direct",
    ),
    url(r"^(?P<event_url_name>[a-zA-Z0-9]+)/inventory/list/$", views.event_list, name="list"),
    # inventory management
    url(r"^manage/inventory/$", views.inventory_list, name="inventory_list"),
    url(r"^manage/inventory/new/$", views.edit_inventory, name="new_inventory"),
    url(r"^manage/inventory/(?P<inventory_pk>[0-9]+)/$", views.edit_inventory, name="edit_inventory"),
    url(r"^manage/inventory/(?P<inventory_pk>[0-9]+)/delete$", views.delete_inventory, name="delete_inventory"),
    url(r"^manage/inventory/(?P<inventory_pk>[0-9]+)/items/$", views.inventory_items, name="inventory_items"),
    # item management
    url(r"^manage/inventory/(?P<inventory_pk>[0-9]+)/items/new/$", views.edit_item, name="new_item"),
    url(
        r"^manage/inventory/(?P<inventory_pk>[0-9]+)/items/" "(?P<item_pk>[0-9]+)/$", views.edit_item, name="edit_item"
    ),
    url(
        r"^manage/inventory/(?P<inventory_pk>[0-9]+)/items/" "(?P<item_pk>[0-9]+)/delete/$",
        views.delete_item,
        name="delete_item",
    ),
]
