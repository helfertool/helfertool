from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from multiselectfield import MultiSelectField

from .event import Event
from .job import Job


class EventAdminRoles(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_RESTRICTED_ADMIN = 'RESTRICTED_ADMIN'
    ROLE_FRONTDESK = 'FRONTDESK'
    ROLE_INVENTORY = 'INVENTORY'
    ROLE_BADGES = 'BADGES'

    ROLE_CHOICES = (
        (ROLE_ADMIN, _('Administrator')),
        (ROLE_RESTRICTED_ADMIN, _('Restricted administrator')),
        (ROLE_FRONTDESK, _('Front desk')),
        (ROLE_INVENTORY, _('Inventory')),
        (ROLE_BADGES, _('Badges')),
    )

    class Meta:
        unique_together = ['event', 'user', ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    roles = MultiSelectField(
        choices=ROLE_CHOICES,
        default=ROLE_ADMIN,
        max_length=250,
        blank=False,
        verbose_name=_("Role"),
    )

    def __str__(self):
        return "{} - {} ({})".format(self.event.name, self.user, ", ".join(self.roles))


class JobAdminRoles(models.Model):
    ROLE_FULL = 'FULL'
    ROLE_DEFAULT = 'DEFAULT'

    ROLE_CHOICES = (
        (ROLE_FULL, _('Full access to all data')),
        (ROLE_DEFAULT, _('Default access')),
    )

    class Meta:
        unique_together = ['job', 'user', ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    roles = MultiSelectField(
        choices=ROLE_CHOICES,
        default=ROLE_DEFAULT,
        max_length=250,
        blank=False,
        verbose_name=_("Role"),
    )

    def __str__(self):
        return "{} - {} ({})".format(self.job, self.user, ", ".join(self.roles))
