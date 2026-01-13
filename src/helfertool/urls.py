from django.conf import settings
from django.urls import include, path, register_converter
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.defaults import page_not_found, server_error, permission_denied, bad_request
from django.views.generic import TemplateView

from .converters import DateConverter

register_converter(DateConverter, "date")

urlpatterns = [
    # django admin interface
    path("manage/django/", admin.site.urls),
    # internationalization
    path("i18n/", include("django.conf.urls.i18n")),
    # django-select2
    path("select2/", include("django_select2.urls")),
    # django-simple-captcha
    path("captcha/", include("captcha.urls")),
    # authentication
    path("login/", auth_views.LoginView.as_view(template_name="helfertool/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # apps without event name in url
    path("manage/settings/", include("toolsettings.urls")),
    path("manage/account/", include("account.urls")),
]

# add oidc urls if enabled
if settings.OIDC_CUSTOM_PROVIDER_NAME is not None:
    urlpatterns += [
        path("oidc/", include("mozilla_django_oidc.urls")),
        path(
            "oidc/failed",
            TemplateView.as_view(template_name="helfertool/login_oidc_failed.html"),
            name="oidc_failed",
        ),
    ]

# this is placed at the end to prevent that event names overwrite other urls
urlpatterns += [
    path("", include("help.urls")),
    path("", include("news.urls")),
    path("", include("registration.urls")),
    path("", include("statistic.urls")),
    path("", include("badges.urls")),
    path("", include("gifts.urls")),
    path("", include("inventory.urls")),
    path("", include("mail.urls")),
    path("", include("prerequisites.urls")),
    path("", include("toollog.urls")),
    path("", include("adminautomation.urls")),
]

# for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL + "public", document_root=settings.MEDIA_ROOT / "public")

    urlpatterns += [
        path("errors/400/", bad_request, {"exception": None}),
        path("errors/403/", permission_denied, {"exception": None}),
        path("errors/404/", page_not_found, {"exception": None}),
        path("errors/500/", server_error),
        path(
            "errors/banned/",
            TemplateView.as_view(template_name="helfertool/login_banned.html"),
        ),
    ]
