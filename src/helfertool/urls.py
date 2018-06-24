from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^djangoadmin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),

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
