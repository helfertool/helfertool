from django.contrib import admin

from .models import Event, Job, Shift, Helper, Duplicate


class HelperAdmin(admin.ModelAdmin):
    search_fields = ['firstname', 'surname', 'email', ]


admin.site.register(Event)
admin.site.register(Job)
admin.site.register(Shift)
admin.site.register(Helper, HelperAdmin)
admin.site.register(Duplicate)
