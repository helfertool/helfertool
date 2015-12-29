from django.contrib import admin

from .models import BadgeSettings, BadgeDesign, BadgePermission

admin.site.register(BadgeSettings)
admin.site.register(BadgeDesign)
admin.site.register(BadgePermission)
