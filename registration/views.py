from django.shortcuts import render, get_object_or_404

from .models import Event
from .forms import RegisterForm

def index(request):
    events = Event.objects.filter(active=True)
    context = {'events': events}
    return render(request, 'registration/index.html', context)

def form(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)

    form = RegisterForm(request.POST or None, event=event)

    if form.is_valid():
        form.save()
        return None

    context = {'event': event,
               'form': form}
    return render(request, 'registration/form.html', context)
