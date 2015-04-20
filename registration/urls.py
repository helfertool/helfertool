from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/$', views.form, name='form'),
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/registered/(?P<helper_id>[a-z0-9\-]+)/$', views.registered, name='registered'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
