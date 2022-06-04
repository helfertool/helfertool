from django.shortcuts import render


def notactive(request):
    return render(request, "prerequisites/not_active.html")
