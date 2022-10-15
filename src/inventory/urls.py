from django.urls import path

from . import views

app_name = "inventory"
urlpatterns = [
    # pages for single event
    path("<slug:event_url_name>/inventory/settings/", views.event_settings, name="event_settings"),
    path("<slug:event_url_name>/inventory/register/", views.register_item, name="register"),
    path(
        "<slug:event_url_name>/inventory/register/<int:item_pk>/",
        views.register_badge,
        name="register_badge",
    ),
    path("<slug:event_url_name>/inventory/take_back/", views.take_back_item, name="take_back"),
    path(
        "<slug:event_url_name>/inventory/take_back/<int:item_pk>/",
        views.take_back_badge,
        name="take_back_badge",
    ),
    path(
        "<slug:event_url_name>/inventory/take_back/<int:item_pk>/direct/",
        views.take_back_direct,
        name="take_back_direct",
    ),
    path("<slug:event_url_name>/inventory/list/", views.event_list, name="list"),
    # inventory management
    path("manage/inventory/", views.inventory_list, name="inventory_list"),
    path("manage/inventory/new/", views.edit_inventory, name="new_inventory"),
    path("manage/inventory/<int:inventory_pk>/", views.edit_inventory, name="edit_inventory"),
    path("manage/inventory/<int:inventory_pk>/delete", views.delete_inventory, name="delete_inventory"),
    path("manage/inventory/<int:inventory_pk>/items/", views.inventory_items, name="inventory_items"),
    # item management
    path("manage/inventory/<int:inventory_pk>/items/new/", views.edit_item, name="new_item"),
    path(
        "manage/inventory/<int:inventory_pk>/items/<int:item_pk>/",
        views.edit_item,
        name="edit_item",
    ),
    path(
        "manage/inventory/<int:inventory_pk>/items/<int:item_pk>/delete/",
        views.delete_item,
        name="delete_item",
    ),
]
