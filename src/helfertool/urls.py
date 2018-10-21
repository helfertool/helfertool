from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    # django admin interface
    url(r'^djangoadmin/', admin.site.urls),

    # internationalization
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # django-select2
    url(r'^select2/', include('django_select2.urls')),

    # authentication
    url(r'^login/$',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'),

    url(r'^logout/$',
        auth_views.LogoutView.as_view(next_page="/"),
        name='logout'),

    # apps
    url(r'^admin/settings/', include('toolsettings.urls')),

    url(r'', include('help.urls')),
    url(r'', include('news.urls')),
    url(r'', include('registration.urls')),
    url(r'', include('statistic.urls')),
    url(r'', include('badges.urls')),
    url(r'', include('gifts.urls')),
    url(r'', include('inventory.urls')),
    url(r'', include('mail.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
