from __future__ import absolute_import

from celery.signals import worker_ready

from helfertool.utils import cache_lock
from .models import Event


@worker_ready.connect  # run on worker startup (when worker is ready to accept tasks)
def setup_event_flags(sender=None, headers=None, body=None, **kwargs):
    with cache_lock("setup_event_flags", sender.app.oid) as acquired:
        if acquired:
            # iterate over all events
            for event in Event.objects.all():
                if event._setup_flags():
                    # True returned means changed -> save changes
                    event.save()
