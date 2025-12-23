from django.db import models


class EventArchiveAutomation(models.Model):
    event = models.OneToOneField(
        "registration.Event",
        on_delete=models.CASCADE,
    )

    last_reminder = models.DateField(
        blank=True,
        null=True,
    )

    exception_date = models.DateField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.event.name
