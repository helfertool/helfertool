from django.db import models
from django.utils.translation import ugettext_lazy as _


class PretixSettings(models.Model):
    event = models.OneToOneField(
        "registration.Event",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.event.name


class PretixItemJobLinkage(models.Model):
    job = models.OneToOneField(
        "registration.Job",
        on_delete=models.CASCADE,
    )

    pretix_item_ref = models.CharField(
        verbose_name=_("Reference to the Pretix item"),
        max_length=100,
    )

    def __str__(self):
        return f"{self.job.name} - {self.pretix_item_ref}"


class PretixOrder(models.Model):
    helper = models.OneToOneField("registration.Helper", null=True, on_delete=models.SET_NULL)

    failed = models.BooleanField(verbose_name=_("Order failed"), default=False)

    pretix_item_ref = models.CharField(
        verbose_name=_("Reference to the Pretix item"),
        max_length=100,
    )

    pretix_order_id = models.CharField(verbose_name=_("Id of the Pretix order"), max_length=20, null=True)

    pretix_order_position_id = models.IntegerField(
        verbose_name=_("Id of the position of the item in the Pretix order"), null=True
    )

    pretix_order_link = models.CharField(verbose_name=_("Public link to the Pretix order"), null=True, max_length=200)

    pretix_ticket_code = models.CharField(
        verbose_name=_("Code printed on the Pretix ticket"), null=True, max_length=200
    )

    def __str__(self):
        return f"{self.helper} - {self.pretix_order_link}"
