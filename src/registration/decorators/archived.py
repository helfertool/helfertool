from django.shortcuts import get_object_or_404, render

from ..models import Event


def archived_not_available(function):
    def _decorated(request, *args, **kwargs):
        event_url_name = kwargs.get("event_url_name")

        if event_url_name:
            event = get_object_or_404(Event, url_name=event_url_name)

            if event.archived:
                context = {"event": event}
                return render(request, "registration/admin/archived_not_available.html", context)

        return function(request, *args, **kwargs)

    return _decorated
