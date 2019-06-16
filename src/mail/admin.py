from django.contrib import admin

from .models import SentMail, MailDelivery

admin.site.register(SentMail)
admin.site.register(MailDelivery)
