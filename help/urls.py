from django.conf.urls import url

from . import views

app_name = 'help'
urlpatterns = [
    url(r'^help/$',
        views.create_issue,
        name='create_issue'),
]
