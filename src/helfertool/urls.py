from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.defaults import page_not_found, server_error, permission_denied, bad_request
from django.views.generic import TemplateView


urlpatterns = [
    # django admin interface
    url(r'^manage/django/', admin.site.urls),

    # internationalization
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # django-select2
    url(r'^select2/', include('django_select2.urls')),

    # authentication
    url(r'^login/$',
        auth_views.LoginView.as_view(template_name='helfertool/login.html'),
        name='login'),

    url(r'^logout/$',
        auth_views.LogoutView.as_view(next_page="/"),
        name='logout'),

    # apps
    url(r'^manage/settings/', include('toolsettings.urls')),
    url(r'^manage/account/', include('account.urls')),
]

# add oidc urls if enabled
if settings.OIDC_CUSTOM_PROVIDER_NAME is not None:
    urlpatterns += [
        url(r'^oidc/', include('mozilla_django_oidc.urls')),
        url(r'^oidc/failed$',
            TemplateView.as_view(template_name='helfertool/login_oidc_failed.html'),
            name='oidc_failed'),
    ]

# this is placed at the end to prevent that event names overwrite other urls
urlpatterns += [
    url(r'', include('help.urls')),
    url(r'', include('news.urls')),
    url(r'', include('registration.urls')),
    url(r'', include('statistic.urls')),
    url(r'', include('badges.urls')),
    url(r'', include('gifts.urls')),
    url(r'', include('inventory.urls')),
    url(r'', include('mail.urls')),
    url(r'', include('prerequisites.urls')),
    url(r'', include('toollog.urls')),
]

# for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL + "public", document_root=settings.MEDIA_ROOT / "public")

    urlpatterns += [
        url(r'errors/400/', bad_request, {'exception': None}),
        url(r'errors/403/', permission_denied, {'exception': None}),
        url(r'errors/404/', page_not_found, {'exception': None}),
        url(r'errors/500/', server_error),
        url(r'errors/banned', TemplateView.as_view(template_name='helfertool/login_banned.html'),),
    ]
