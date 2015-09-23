from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import date as date_f
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Shift(models.Model):
    """ A shift of one job.

    Columns:
        :job: job of this shift
        :begin: begin of the shift
        :end: end of the shift
        :number: number of people
        :blocked: shift is blocked, if the job is public
    """
    class Meta:
        ordering = ['job', 'begin', 'end']

    job = models.ForeignKey(
        'Job',
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

    def __str__(self):
        date = date_f(localtime(self.begin), 'DATETIME_FORMAT')
        return "%s %s (%s)" % (self.job.name, date, self.job.event)

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

        return int(round(self.num_helpers() / self.number * 100, 0))


@receiver(pre_delete, sender=Shift, dispatch_uid='shift_delete')
def shift_delete(sender, instance, using, **kwargs):
    """ Delete helpers without shifts, when a shift is deleted.

    This is a signal handler, that is called, when a shift is deleted. It
    deletes all helpers, that are only registered for this single shift.
    """
    # delete helpers, that have only one shift, when this shift is deleted
    for helper in instance.helper_set.all():
        if helper.shifts.count() == 1:
            helper.delete()
