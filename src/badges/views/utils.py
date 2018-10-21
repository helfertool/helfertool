from django.shortcuts import render


def notactive(request):
    return render(request, 'badges/not_active.html')
