from django.shortcuts import render


def notactive(request):
    return render(request, 'gifts/gifts_not_active.html')
