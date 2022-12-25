from django.contrib import admin

from .models import PretixSettings, PretixItemJobLinkage, PretixOrder

admin.site.register(PretixSettings)
admin.site.register(PretixItemJobLinkage)
admin.site.register(PretixOrder)
