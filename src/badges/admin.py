from django.contrib import admin

from .models import BadgeSettings, BadgeDesign, BadgePermission, BadgeRole, Badge, SpecialBadges


class SpecialBadgesAdmin(admin.ModelAdmin):
    exclude = ["badges"]  # if django admin handles this field, it overwrites our m2m changes


admin.site.register(Badge)
admin.site.register(BadgeSettings)
admin.site.register(BadgeDesign)
admin.site.register(BadgePermission)
admin.site.register(BadgeRole)
admin.site.register(SpecialBadges, SpecialBadgesAdmin)
