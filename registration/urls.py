from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # login, logout
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='logout'),

    # registration
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/$', views.form, name='form'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/registered/(?P<helper_id>[a-z0-9\-]+)/$',
        views.registered, name='registered'),

    # admin
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/admin/$', views.admin, name='admin'),

    # helpers
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/$', views.helpers, name='helpers'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/(?P<job_pk>[0-9]+)$', views.helpers, name='jobhelpers'),

    # excel
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/excel/all$', views.excel, name='excel'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/excel/(?P<job_pk>[0-9]+)$', views.excel, name='jobexcel'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
