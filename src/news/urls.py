from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "news"
urlpatterns = [
    # management
    path("manage/news/", views.send, name="send"),
    path("manage/news/remove/", views.remove, name="remove"),
    path("manage/news/failures/", views.failures, name="failures"),
    # subscribe and unsubcribe
    path("subscribe/", views.subscribe, name="subscribe"),
    path("subscribe/done/", TemplateView.as_view(template_name="news/subscribe_done.html"), name="subscribe_done"),
    path("subscribe/<uuid:token>/", views.subscribe_confirm, name="subscribe_confirm"),
    # empty tokens are allowed since this is used to generate the link once
    # and add the specific tokens
    # empty tokens are handled in the view with an 404
    path("unsubscribe/", views.unsubscribe, name="unsubscribe_empty"),
    path("unsubscribe/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
    path(
        "unsubscribe/done/",
        TemplateView.as_view(template_name="news/unsubscribe_done.html"),
        name="unsubscribe_done",
    ),
]
