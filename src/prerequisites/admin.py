from django.contrib import admin

from .models import Prerequisite, FulfilledPrerequisite

admin.site.register(Prerequisite)
admin.site.register(FulfilledPrerequisite)
