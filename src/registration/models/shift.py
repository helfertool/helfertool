from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import date as date_f
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _

from collections import OrderedDict
from copy import deepcopy
from datetime import datetime

import math


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
        on_delete=models.CASCADE,
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

    def date(self):
        """ Returns the day on which the shifts begins. """
        return localtime(self.begin).date()

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

    def helpers_percent_5percent(self):
        """
        Returns the percentage of registered helpers in 5% steps.
        So the returned value is between 0 and 20 (including both values).

        This is used to generate the CSS class names defined in style.css.
        Therefore, inline CSS can be avoided.
        """
        percent = self.helpers_percent()
        return math.ceil(percent / 5)

    def helpers_percent_vacant_5percent(self):
        """
        Same as `helpers_percent_5percent`, but for the missing helpers.
        """
        return 20 - self.helpers_percent_5percent()

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

    def duplicate(self, new_date=None, new_job=None, gift_set_mapping=None):
        """ Duplicate a shift. There are multiple possibilities:

        * Shift is copied to new day in same job: set new_date
        * Shift is copied to new job in same event: set new_job
        * Shift is copied to new event: set new_job and gift_set_mapping
        """
        new_shift = deepcopy(self)
        new_shift.pk = None
        new_shift.archived_number = 0

        # maybe shift is copied to new job
        if new_job:
            new_shift.job = new_job

            # if shift is copied to new event, move begin and end time according to diff in event dates
            if self.job.event != new_job.event:
                diff = new_job.event.date - self.job.event.date
                new_shift.begin += diff
                new_shift.end += diff

        # maybe just the date is changed
        if new_date:
            new_shift.move_date(new_date)

        # now save that
        new_shift.save()

        # and finally set the gifts again
        for gift in self.gifts.all():
            if gift_set_mapping:
                new_shift.gifts.add(gift_set_mapping[gift])
            else:
                new_shift.gifts.add(gift)

        return new_shift

    def move_date(self, new_date):
        # current begin and end in local time
        old_begin_localtime = localtime(self.begin)
        old_end_localtime = localtime(self.end)

        # move date alone without chainging time
        diff_days = new_date - old_begin_localtime.date()

        new_begin_date = old_begin_localtime.date() + diff_days
        new_end_date = old_end_localtime.date() + diff_days

        # set time separately (10 am should always be 10 am, also when a time change is between old and new date)
        begin_time = old_begin_localtime.time()
        end_time = old_end_localtime.time()

        self.begin = datetime.combine(new_begin_date, begin_time)
        self.end = datetime.combine(new_end_date, end_time)


@receiver(pre_delete, sender=Shift)
def shift_deleted(sender, instance, using, **kwargs):
    # m2m_changed does not trigger here, so remote the helpers before the shift is deleted
    for helper in instance.helper_set.all():
        helper.shifts.remove(instance)
