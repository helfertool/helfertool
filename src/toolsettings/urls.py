from django.urls import path

from . import views

app_name = "toolsettings"
urlpatterns = [
    path("templates/", views.templates, name="templates"),
    path("templates/about/", views.template_about, name="template_about"),
    path("templates/privacy/", views.template_privacy, name="template_privacy"),
    path("templates/login/", views.template_login, name="template_login"),
    path("templates/add_user/", views.template_add_user, name="template_add_user"),
    path("templates/newsletter/", views.template_newsletter, name="template_newsletter"),
    path("check/", views.check, name="check"),
]
