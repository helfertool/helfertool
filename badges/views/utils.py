from django.shortcuts import render


def notactive(request):
    return render(request, 'badges/badges_not_active.html')
