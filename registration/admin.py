from django.contrib import admin

from .models import Event, Job, Shift, Helper, BadgeSettings, BadgeDesign, \
    BadgePermission

admin.site.register(Event)
admin.site.register(Job)
admin.site.register(Shift)
admin.site.register(Helper)
admin.site.register(BadgeSettings)
admin.site.register(BadgeDesign)
admin.site.register(BadgePermission)
