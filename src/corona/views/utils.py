from django.shortcuts import render


def notactive(request):
    return render(request, "corona/not_active.html")
