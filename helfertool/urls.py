from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^djangoadmin/', include(admin.site.urls)),

    url(r'', include('registration.urls')),
    url(r'', include('badges.urls')),
    url(r'', include('gifts.urls')),
    url(r'', include('mail.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
