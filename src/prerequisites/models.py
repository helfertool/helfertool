from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_bleach.models import BleachField


class Prerequisite(models.Model):
    """
    Prerequisite for one or many jobs

    Columns:
        :name: Name (in all internal views)
        :long_name: Name that is visible for helpers
        :description: Description
        :helper_can_set: Helpers can specify at registration whether they have this prerequisite
    """

    class Meta:
        unique_together = ('event', 'name', )

    event = models.ForeignKey(
        'registration.Event',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
        help_text="The prerequisite's name in all internal views"
    )

    long_name = models.CharField(
        max_length=200,
        verbose_name=_("Registration name"),
        help_text="Name displayed for helpers at registration"
    )

    description = BleachField(
        blank=True,
        verbose_name=_("Description"),
    )

    helper_can_set = models.BooleanField(
        default=False,
        verbose_name=_("Helpers can specify this prerequisite at registration"),
    )


class FulfilledPrerequisite(models.Model):
    """
    Link between helpers and prerequisites

    Columns:
        :has_prerequisite: The helper fulfils this prerequisite
    """

    class Meta:
        pass

    prerequisite = models.ForeignKey(
        'prerequisites.Prerequisite',
        on_delete=models.CASCADE,
    )

    helper = models.ForeignKey(
        'registration.Helper',
        on_delete=models.CASCADE,
    )

    has_prerequisite = models.BooleanField(
        default=False,
        verbose_name=_("Helper fulfils this prerequisite")
    )
