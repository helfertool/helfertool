from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    # account
    path("", views.view_user, name="view_user"),
    path("<int:user_pk>/", views.view_user, name="view_user"),
    path("<int:user_pk>/edit/", views.edit_user, name="edit_user"),
    path("<int:user_pk>/delete/", views.delete_user, name="delete_user"),
    path("<int:user_pk>/merge/", views.merge_user, name="merge_user"),
    path("new/", views.add_user, name="add_user"),
    path("list/", views.list_users, name="list_users"),
    # agreements
    path("check/", views.check_user_agreement, name="check_user_agreement"),
    path("check/<int:agreement_pk>/", views.handle_user_agreement, name="handle_user_agreement"),
    path("agreements/", views.list_agreements, name="list_agreements"),
    path("agreements/new/", views.edit_agreement, name="new_agreement"),
    path("agreements/<int:agreement_pk>/", views.edit_agreement, name="edit_agreement"),
    path("agreements/<int:agreement_pk>/delete/", views.delete_agreement, name="delete_agreement"),
]
