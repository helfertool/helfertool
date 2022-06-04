from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField


class ContactTracingData(models.Model):
    event = models.ForeignKey(
        "registration.Event",
        on_delete=models.CASCADE,
    )

    helper = models.OneToOneField(
        "registration.Helper",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    street = models.CharField(
        max_length=250,
        verbose_name=_("Street and house number"),
    )

    zip = models.CharField(
        max_length=250,
        verbose_name=_("ZIP code"),
    )

    city = models.CharField(
        max_length=250,
        verbose_name=_("City"),
    )

    country = CountryField(
        verbose_name=_("Country"),
    )

    agreed = models.BooleanField(
        default=False,
        verbose_name=_("I assure that the provided data is correct."),
    )

    def __str__(self):
        return "{} - {}".format(self.event, self.helper.full_name)
