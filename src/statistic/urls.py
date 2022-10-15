from django.urls import path

from . import views

app_name = "statistic"
urlpatterns = [
    path("<slug:event_url_name>/statistics/", views.overview, name="overview"),
    path("<slug:event_url_name>/statistics/chart/timeline/", views.chart_timeline, name="chart_timeline"),
    path("<slug:event_url_name>/statistics/chart/helpers/", views.chart_helpers, name="chart_helpers"),
    path("<slug:event_url_name>/statistics/chart/shifts/", views.chart_shifts, name="chart_shifts"),
    path(
        "<slug:event_url_name>/statistics/chart/eatinghabits/",
        views.chart_nutrition,
        name="chart_nutrition",
    ),
    path("<slug:event_url_name>/shirts/", views.shirts, name="shirts"),
    path("<slug:event_url_name>/nutrition/", views.nutrition, name="nutrition"),
]
