from django.shortcuts import render


def notactive(request):
    return render(request, 'inventory/inventory_not_active.html')
