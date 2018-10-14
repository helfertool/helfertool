from django.conf.urls import url

from . import views

from django.views.generic import TemplateView

app_name = 'toolsettings'
urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name='toolsettings/index.html'),
        name='index'),

    url(r'^templates/about/$',
        views.template_about,
        name='template_about'),

    url(r'^templates/privacy/$',
        views.template_privacy,
        name='template_privacy'),

    url(r'^templates/login/$',
        views.template_login,
        name='template_login'),

    url(r'^check/$',
        views.check,
        name='check'),
]
