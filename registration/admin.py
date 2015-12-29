from django.contrib import admin

from .models import Event, Job, Shift, Helper

admin.site.register(Event)
admin.site.register(Job)
admin.site.register(Shift)
admin.site.register(Helper)
