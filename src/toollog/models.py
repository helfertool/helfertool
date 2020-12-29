from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.template.defaultfilters import date as date_f
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from registration.models import Event, Helper


class LogEntry(models.Model):
    """ Log entry which is stored by DatabaseHandler.

    The entries are only stored as long as the event exists.

    Columns:
        :timestamp: timestamp of the log entry
        :level: log level (INFO, WARN, ...)
        :message: log message
        :event: related event (optional)
        :helper: related helper (optional)
        :user: the user that emitted the event (optional)
        :extra: further data stored as JSON
        :app: Helfertool component that emitted the event (registration, mail, ...)
    """

    class Meta:
        ordering = ['-timestamp']

    timestamp = models.DateTimeField(
        verbose_name=_("Timestamp")
    )

    level = models.CharField(
        max_length=16,
        verbose_name=_("Log level")
    )

    message = models.CharField(
        max_length=512,
        verbose_name=_("Message"),
    )

    event = models.ForeignKey(
        Event,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Event"),
    )

    helper = models.ForeignKey(
        Helper,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # keep logs for deleted helpers (-> event admins see that helper was deleted)
        verbose_name=_("Helper"),
    )

    user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,  # keep logs for deleted users
        verbose_name=_("User"),
        related_name="helfertoollogentry"
    )

    extras = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Extra data"),
        encoder=DjangoJSONEncoder,  # necessary to serialize UUIDs
    )

    module = models.CharField(
        max_length=128,
        verbose_name=_("Helfertool module"),
    )

    def __str__(self):
        return "{} - {} - {}".format(
            date_f(localtime(self.timestamp), 'DATETIME_FORMAT'),
            self.level,
            self.message,
        )
