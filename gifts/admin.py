from django.contrib import admin

from .models import Gift, GiftSet, IncludedGift, HelpersGifts, \
    DeservedGiftSet

class IncludedGiftInline(admin.TabularInline):
    model = IncludedGift
    extra = 1

class GiftSetAdmin(admin.ModelAdmin):
    inlines = (IncludedGiftInline, )

admin.site.register(Gift)
admin.site.register(GiftSet, GiftSetAdmin)
admin.site.register(HelpersGifts)
admin.site.register(DeservedGiftSet)
