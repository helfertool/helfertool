from django.shortcuts import render


def notactive(request):
    return render(request, "inventory/not_active.html")
