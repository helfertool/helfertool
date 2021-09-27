from django.contrib import admin

from .models import CoronaSettings, ContactTracingData

admin.site.register(CoronaSettings)
admin.site.register(ContactTracingData)
