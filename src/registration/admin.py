from django.contrib import admin

from .models import Event, EventAdminRoles, EventArchive, Job, Shift, Helper, Duplicate, HelperShift


class HelperAdmin(admin.ModelAdmin):
    search_fields = ['firstname', 'surname', 'email', ]


admin.site.register(Event)
admin.site.register(EventAdminRoles)
admin.site.register(EventArchive)
admin.site.register(Job)
admin.site.register(Shift)
admin.site.register(Helper, HelperAdmin)
admin.site.register(Duplicate)
admin.site.register(HelperShift)
