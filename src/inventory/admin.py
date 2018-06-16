from django.contrib import admin

from .models import Inventory, Item, UsedItem, InventorySettings

admin.site.register(Inventory)
admin.site.register(Item)
admin.site.register(UsedItem)
admin.site.register(InventorySettings)
