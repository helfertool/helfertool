import logging
import json


class HelfertoolDatabaseHandler(logging.Handler):
    """
    A Log handler to store logs into the database, resolving extras as foreign keys
    """

    def __init__(self, *args, **kwargs):
        super(HelfertoolDatabaseHandler, self).__init__(*args, **kwargs)


    def get_extra(self, extras, key, classname):
        """
        Extract the key with the classname from the extras dictionary.

        returns an object of type classname or the primary key of the object,
        both storable in a ForeignKey-object
        """
        if key in extras:
            if isinstance(extras[key], classname):
                keypk = key + "_pk"
                if keypk in extras and  extras[key].pk != extras[keypk]:
                    raise ValueError("Inconsistenc in log extras: %s should contain the pk of %s", key, keypk)
                return extras[key]

        keypk = key + "_pk"
        if keypk in extras:
            return extras[keypk]

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
        dbrecord.messsage = record.getMessage()
        dbrecord.time = record.created
        dbrecord.app = record.name

        extras = record.extras

        # dissect the extras
        dbrecord.event = self.get_extra(extras, 'event', Event)
        dbrecord.user = self.get_extra(extras, 'user', User)
        dbrecord.helper = self.get_extra(extras, 'helper', Helper)

        # Remove already parsed fields
        extras = dict(filter(lambda key: key not in ['event', 'event_pk', 'user', 'user_pk', 'helper', 'helper_pk']))

        # Change this for migrating to JSONField
        dbrecord.extras = json.dumps(extras)

        dbrecord.save()