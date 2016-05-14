from django.contrib import admin

from .models import Gift, GiftSet, HelpersGifts, DeservedGiftSet

admin.site.register(Gift)
admin.site.register(GiftSet)
admin.site.register(HelpersGifts)
admin.site.register(DeservedGiftSet)
