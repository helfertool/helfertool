from django.contrib import admin

from .models import Gift, GiftSet, GiftSetElement, HelpersGifts, \
    DeservedGiftSet

class GiftSetElementInline(admin.TabularInline):
    model = GiftSetElement
    extra = 1

class GiftSetAdmin(admin.ModelAdmin):
    inlines = (GiftSetElementInline, )

admin.site.register(Gift)
admin.site.register(GiftSet, GiftSetAdmin)
admin.site.register(HelpersGifts)
admin.site.register(DeservedGiftSet)
