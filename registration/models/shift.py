from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import date as date_f
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict

from .helper import Helper



@python_2_unicode_compatible
class Shift(models.Model):
    """ A shift of one job.

    Columns:
        :job: job of this shift
        :begin: begin of the shift
        :end: end of the shift
        :number: number of people
        :blocked: shift is blocked, if the job is public
        :name: name of the shift (optional)
    """
    class Meta:
        ordering = ['job', 'begin', 'end']

    job = models.ForeignKey(
        'Job',
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name (optional)"),
        default="",
        blank=True,
    )

    begin = models.DateTimeField(
        verbose_name=_("Begin"),
    )

    end = models.DateTimeField(
        verbose_name=_("End"),
    )

    number = models.IntegerField(
        default=0,
        verbose_name=_("Number of helpers"),
        validators=[MinValueValidator(0)],
    )

    blocked = models.BooleanField(
        default=False,
        verbose_name=_("If the job is publicly visible, "
                       "the shift is blocked."),
    )

    gifts = models.ManyToManyField(
        'gifts.GiftSet',
        verbose_name=_("Gifts"),
        blank=True,
    )

    def __str__(self):
        if self.name:
            return "%s, %s, %s" % (self.job.name, self.name, self.time())
        else:
            return "%s, %s" % (self.job.name, self.time())

    def time(self):
        """ Returns a string representation of the begin and end time.

        The begin contains the date and time, the end only the time.
        """
        return "%s, %s - %s" % (date_f(localtime(self.begin), 'DATE_FORMAT'),
                                date_f(localtime(self.begin), 'TIME_FORMAT'),
                                date_f(localtime(self.end), 'TIME_FORMAT'))

    def time_hours(self):
        """ Returns a string representation of the begin and end time.

        Only the time is used, the date is not shown.
        """
        return "%s - %s" % (date_f(localtime(self.begin), 'TIME_FORMAT'),
                            date_f(localtime(self.end), 'TIME_FORMAT'))

    def num_helpers(self):
        """ Returns the current number of helpers- """
        return self.helper_set.count()

    def is_full(self):
        """ Check if the shift is full and return a boolean. """
        return self.num_helpers() >= self.number

    def helpers_percent(self):
        """ Calculate the percentage of registered helpers and returns an int.

        If the maximal number of helpers for a shift is 0, 0 is returned.
        """
        if self.number == 0:
            return 0

        return int(round(float(self.num_helpers()) / self.number * 100.0, 0))

    @property
    def shirt_sizes(self):
        # data structure
        shirts = OrderedDict()
        for size, name in Helper.SHIRT_CHOICES:
            shirts.update({name: 0})

        # collect all sizes, this must be the first shift of the helper
        for helper in self.helper_set.all():
            if helper.first_shift == self:
                tmp = shirts[helper.get_shirt_display()]
                shirts.update({helper.get_shirt_display(): tmp+1})

        return shirts

@receiver(pre_delete, sender=Shift)
def shift_deleted(sender, instance, using, **kwargs):
    """
    TODO: remove in django 1.10 since m2m_changed sends signal
    """
    for helper in instance.helper_set.all():
        helper.shifts.remove(instance)
