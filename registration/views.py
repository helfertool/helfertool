from django.shortcuts import render, get_object_or_404

from .models import Event

def index(request):
    events = Event.objects.filter(active=True)
    context = {'events': events}
    return render(request, 'registration/index.html', context)

def register(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)
