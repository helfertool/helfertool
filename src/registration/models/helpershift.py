from django.db import models
from django.utils.translation import ugettext_lazy as _


class HelperShift(models.Model):
    """
    n-m relation between helper and shift.

    Columns:

        :present: Flag set when the helper is there (manually or automatically)
        :absent: Flag manually set if the helper did not attend at his shift
    """
    class Meta:
        unique_together = ('helper', 'shift',)

    helper = models.ForeignKey(
        'Helper',
        on_delete=models.CASCADE,
    )

    shift = models.ForeignKey(
        'Shift',
        on_delete=models.CASCADE,
    )

    present = models.BooleanField(
        default=False,
        verbose_name=_("Present"),
        help_text=_("Helper was at shift")
    )

    manual_presence = models.BooleanField(
        default=False,
        editable=False,
        help_text="presence was manually set"
    )