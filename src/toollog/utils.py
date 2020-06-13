import logging
import json

from django.db import models


class HelfertoolDatabaseHandler(logging.Handler):
    """
    A Log handler to store logs into the database, resolving extras as foreign keys
    """

    def __init__(self, *args, **kwargs):
        super(HelfertoolDatabaseHandler, self).__init__(*args, **kwargs)

    def get_extra(self, record, key, classname):
        """
        Extract the key with the classname from the extras dictionary.

        returns an object of type classname or the primary key of the object,
        both storable in a ForeignKey-object
        """
        if key in record.__dict__ and isinstance(record.__dict__[key], classname):
            keypk = key + "_pk"
            if keypk in record.__dict__ and record.__dict__[key].pk != record.__dict__[keypk]:
                raise ValueError("Inconsistenc in log extras: %s should contain the pk of %s" % (key, keypk))
            return record.__dict__[key]

        keypk = key + "_pk"
        if keypk in record.__dict__:
            return record.__dict__[keypk]

        return None

    def emit(self, record):
        """
        Store the record into the database
        will resolve the following fields from 'extras':

        - 'event': the Event used
        - 'user': the logged in User that emitted the event that created the log
        - 'helper': the helper that issued the log

        All of the above may be suffixed with _pk to refer to only a key, not an object
        If the non-_pk version is only a string, the _pk version is preferred.
        If it is an object of the expected type the _pk version will be used to verify.
        (since it is often used to store only the name)

        It will also concatenate other, extra information as an extra-field as json.
        """

        # We have to import Models here, because of initialization dependencies within django
        # this module is loaded during settings.py, thereby no database is available
        from django.contrib.auth.models import User
        from registration.models import Event, Helper
        from toollog.models import HelfertoolLogEntry

        # Extract information from the record
        dbrecord = HelfertoolLogEntry()
        dbrecord.level = record.levelname
        dbrecord.message = record.getMessage()
        dbrecord.time = record.created
        dbrecord.app = record.name

        # dissect the extras
        dbrecord.event = self.get_extra(record, 'event', Event)
        dbrecord.user = self.get_extra(record, 'user', User)
        dbrecord.helper = self.get_extra(record, 'helper', Helper)

        # remove all standard arfs from the record
        extra = {k: v for k, v in record.__dict__.items() if k not in [
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module',
            'exc_info', 'exc_text', 'stack_info', 'funcName', 'lineno',
            'created', 'asctime', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'extras', 'message']
        }

        extra.pop('event', None)
        extra.pop('event_pk', None)
        extra.pop('user', None)
        extra.pop('user_pk', None)
        extra.pop('helper', None)
        extra.pop('helper_pk', None)

        # clean up keys
        for k in extra:
            if isinstance(extra[k], models.Model):
                extra[k] = extra[k].pk
            else:
                extra[k] = str(extra[k])

        # Change this for migrating to JSONField
        dbrecord.extra = json.dumps(extra)

        dbrecord.save()
