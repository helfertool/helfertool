from django.urls import path

from . import views

app_name = "gifts"
urlpatterns = [
    #
    # list
    #
    path("<slug:event_url_name>/gifts/", views.list, name="list"),
    #
    # edit gifts
    #
    path("<slug:event_url_name>/gifts/gift/add/", views.edit_gift, name="add_gift"),
    path("<slug:event_url_name>/gifts/gift/<int:gift_pk>/", views.edit_gift, name="edit_gift"),
    path(
        "<slug:event_url_name>/gifts/gift/<int:gift_pk>/delete/",
        views.delete_gift,
        name="delete_gift",
    ),
    #
    # edit gift sets
    #
    path("<slug:event_url_name>/gifts/giftset/add/", views.edit_gift_set, name="add_gift_set"),
    path(
        "<slug:event_url_name>/gifts/giftset/<int:gift_set_pk>/",
        views.edit_gift_set,
        name="edit_gift_set",
    ),
    path(
        "<slug:event_url_name>/gifts/giftset/<int:gift_set_pk>/delete/",
        views.delete_gift_set,
        name="delete_gift_set",
    ),
    #
    # open deposits
    #
    path("<slug:event_url_name>/gifts/deposit/", views.list_deposit, name="list_deposit"),
    #
    # shirts that need to be bought
    #
    path("<slug:event_url_name>/gifts/shirts/", views.list_shirts, name="list_shirts"),
    #
    # set present flag for complete shifts
    #
    path(
        "<slug:event_url_name>/gifts/present/<int:shift_pk>/",
        views.set_present,
        name="set_present",
    ),
]
