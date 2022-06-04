from django.db import models
from django.utils.translation import ugettext_lazy as _


class HelperShift(models.Model):
    """
    n-m relation between helper and shift.

    This model then can be used by other apps to "attach" more data with OneToOne fields and signals.

    The fields `present` and `manual_presence` belong to the gifts app. They are directly inserted here as it
    would be too complicated to add another model for just two booleans. Additionally, this has the advantage
    that the `present` flag can directly used by other apps.

    Columns:
        :helper: The helper
        :shift: The shift
        :timestamp: Timestamp when the helper registered for this shift
        :present: Flag set when the helper is there (manually or automatically)
        :manual_presence: `present` flag was manually set
    """

    class Meta:
        unique_together = (
            "helper",
            "shift",
        )

    helper = models.ForeignKey(
        "Helper",
        on_delete=models.CASCADE,
    )

    shift = models.ForeignKey(
        "Shift",
        on_delete=models.CASCADE,
    )

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Registration time for this shift"))

    present = models.BooleanField(default=False, verbose_name=_("Present"), help_text=_("Helper was at shift"))

    manual_presence = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_("Presence was manually set"),
    )

    def __str__(self):
        return "{} - {} - {}".format(self.helper.event, self.helper, self.shift)
