from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='logout'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/$', views.form, name='form'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/details/$', views.details, name='details'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/registered/(?P<helper_id>[a-z0-9\-]+)/$',
        views.registered, name='registered'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
