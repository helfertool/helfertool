from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

app_name = "news"
urlpatterns = [
    # management
    url(r"^manage/news/$", views.send, name="send"),
    url(r"^manage/news/remove/$", views.remove, name="remove"),
    # subscribe and unsubcribe
    url(r"^subscribe/$", views.subscribe, name="subscribe"),
    url(r"^subscribe/done/$", TemplateView.as_view(template_name="news/subscribe_done.html"), name="subscribe_done"),
    url(r"^subscribe/(?P<token>[0-9a-f\-]*)/$", views.subscribe_confirm, name="subscribe_confirm"),
    # empty tokens are allowed since this is used to generate the link once
    # and add the specific tokens
    # empty tokens are handled in the view with an 404
    url(r"^unsubscribe/(?P<token>[0-9a-f\-]*)/$", views.unsubscribe, name="unsubscribe"),
    url(
        r"^unsubscribe/done/$",
        TemplateView.as_view(template_name="news/unsubscribe_done.html"),
        name="unsubscribe_done",
    ),
]
