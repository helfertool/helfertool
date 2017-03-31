from .models import Inventory

def is_inventory_admin(user):
    return Inventory.objects.filter(admins__exact=user).exists()
