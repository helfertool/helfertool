from django.shortcuts import render


def notactive(request):
    return render(request, "gifts/not_active.html")
