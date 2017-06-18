from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import date as date_f
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict
from copy import deepcopy

from .helper import Helper


class Shift(models.Model):
    """ A shift of one job.

    Columns:
        :job: job of this shift
        :begin: begin of the shift
        :end: end of the shift
        :number: number of people
        :blocked: shift is blocked, if the job is public
        :hidden: shift is not displayed publicly
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
        verbose_name=_("The shift is blocked and displayed as full."),
    )

    hidden = models.BooleanField(
        default=False,
        verbose_name=_("The shift is not visible."),
    )

    gifts = models.ManyToManyField(
        'gifts.GiftSet',
        verbose_name=_("Gifts"),
        blank=True,
    )

    archived_number = models.IntegerField(
        default=0,
        verbose_name=_("Number of registered helpers for archived event"),
    )

    def __str__(self):
        if self.name:
            return "%s, %s, %s" % (self.job.name, self.name,
                                   self.time_with_day())
        else:
            return "%s, %s" % (self.job.name, self.time_with_day())

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

    def time_with_day(self):
        """ Returns a string representation of the day.

        If the shift is on two days only the name of the first day is returned.
        """
        day = date_f(localtime(self.begin), "l")
        return "{}, {}".format(day, self.time())

    def num_helpers(self):
        """
        Returns the current number of helpers, but 0 if event is archived.
        """
        return self.helper_set.count()

    def num_helpers_archived(self):
        """ Returns the current number of helpers- """
        if self.job.event.archived:
            return self.archived_number
        else:
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

        num = self.num_helpers_archived()
        return int(round(float(num) / self.number * 100.0, 0))

    @property
    def shirt_sizes(self):
        # data structure
        shirts = OrderedDict()
        for size, name in self.job.event.get_shirt_choices():
            shirts.update({name: 0})

        # collect all sizes, this must be the first shift of the helper
        for helper in self.helper_set.all():
            if helper.first_shift == self:
                tmp = shirts[helper.get_shirt_display()]
                shirts.update({helper.get_shirt_display(): tmp+1})

        return shirts

    def duplicate(self, new_job, gift_set_mapping):
        new_shift = deepcopy(self)
        new_shift.pk = None
        new_shift.job = new_job
        new_shift.archived_number = 0

        # move begin and end time according to diff in event dates
        diff = new_job.event.date - self.job.event.date
        new_shift.begin += diff
        new_shift.end += diff

        new_shift.save()

        for gift in self.gifts.all():
            new_shift.gifts.add(gift_set_mapping[gift])

        return new_shift


@receiver(pre_delete, sender=Shift)
def shift_deleted(sender, instance, using, **kwargs):
    """
    TODO: remove in django 1.10 since m2m_changed sends signal
    """
    for helper in instance.helper_set.all():
        helper.shifts.remove(instance)
