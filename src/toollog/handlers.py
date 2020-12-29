from django.db import IntegrityError
from django.utils.timezone import make_aware

from datetime import datetime

import logging

from .utils import get_extras


class DatabaseHandler(logging.Handler):
    """
    A log handler to store logs into the database.

    Currently, only log entries that belong to an event are stored in the database.
    All other log entries are available in the log files / via syslog.
    """
    def __init__(self, *args, **kwargs):
        self._logentry_model = None

        super(DatabaseHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        # the handler is initialized by django before the database setup, so the import would fail
        # therefore, we do it here dynamically when necessary - but only once
        if not self._logentry_model:
            from .models import LogEntry
            self._logentry_model = LogEntry

        # get the event, helper and user if they are stored in the entry
        event = record.event if hasattr(record, 'event') else None
        if not event:
            return

        helper = record.helper if hasattr(record, 'helper') else None
        user = record.user if hasattr(record, 'user') else None

        # create the entry
        entry = self._logentry_model(
            timestamp=make_aware(datetime.fromtimestamp(record.created)),
            level=record.levelname,
            message=record.getMessage(),
            event=event,
            helper=helper,
            user=user,
            extras=get_extras(record),
            module=record.name,
        )

        try:
            entry.save()
        except ValueError:
            # if the event is deleted, we cannot save. we only store logs for existing events,
            # so we can discard this event (deletions are still logged via syslog / in files if container is used)
            pass
        except IntegrityError:
            # if a helper is deleted, the helper object is still there while we prepare the entry.
            # on save, the helper may already be deleted, so we have a foreign key error.
            entry.helper = None
            entry.save()
