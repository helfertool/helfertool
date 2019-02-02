from django.contrib import admin

from .models import Agreement, UserAgreement


admin.site.register(Agreement)
admin.site.register(UserAgreement)
