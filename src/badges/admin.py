from django.contrib import admin

from .models import BadgeSettings, BadgeDesign, BadgePermission, BadgeRole, \
    Badge

admin.site.register(Badge)
admin.site.register(BadgeSettings)
admin.site.register(BadgeDesign)
admin.site.register(BadgePermission)
admin.site.register(BadgeRole)
