from django.urls import path

from . import views

app_name = "help"
urlpatterns = [
    path("help/", views.create_issue, name="create_issue"),
]
