from django.conf.urls import url

from . import views

app_name = 'statistic'
urlpatterns = [
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/statistics/$',
        views.overview,
        name='overview'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/statistics/chart/timeline/$',
        views.chart_timeline,
        name='chart_timeline'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/shirts/$',
        views.shirts,
        name='shirts'),
]
