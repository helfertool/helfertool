from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_bleach.models import BleachField
from django.utils.timezone import localtime

from collections import OrderedDict
from copy import deepcopy

from badges.models import BadgeDefaults


class Job(models.Model):
    """ A job that contains min. 1 shift.

    Columns:
        :event: event of this job
        :name: name of the job, e.g, Bierstand
        :infection_instruction: is an instruction for the handling of food
                                necessary?
        :description: longer description of the job
        :job_admins: users, that can see and edit the helpers
        :public: job is visible publicly
        :badge_design: badge design for this job
    """

    event = models.ForeignKey(
        'Event',
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    public = models.BooleanField(
        default=False,
        verbose_name=_("This job is visible publicly"),
    )

    infection_instruction = models.BooleanField(
        default=False,
        verbose_name=_("Instruction for the handling of food necessary"),
    )

    description = BleachField(
        blank=True,
        verbose_name=_("Description"),
    )

    job_admins = models.ManyToManyField(
        User,
        blank=True,
    )

    coordinators = models.ManyToManyField(
        'Helper',
        blank=True,
    )

    badge_defaults = models.OneToOneField(
        BadgeDefaults,
        blank=True,
        null=True,
    )

    archived_number_coordinators = models.IntegerField(
        default=0,
        verbose_name=_("Number of coordinators for archived event"),
    )

    def __str__(self):
        return "%s" % self.name

    @property
    def num_coordinators(self):
        if self.event.archived:
            return self.archived_number_coordinators
        else:
            return self.coordinators.count()

    def is_admin(self, user):
        """ Check, if a user is admin of this job and returns a boolean.

        Superusers and admins of the event are also admins of a shift.

        :param user: the user
        :type user: :class:`django.contrib.auth.models.User`

        :returns: True or False
        """
        return self.event.is_admin(user) or \
            self.job_admins.filter(pk=user.pk).exists()

    def helpers_and_coordinators(self):
        helpers = Helper.objects.filter(shifts__job=self).distinct()
        coordinators = self.coordinators.distinct()
        return helpers | coordinators

    def shifts_by_day(self, shifts=None, show_hidden=True):
        """ Returns all shifts grouped sorted by day and sorted by time.

        The result is a dict with date objects as keys. Each item of the
        dictionary is a OrderedDict of shifts.

        :param shifts: list of shifts, must be shifts of this job (optional)
        :type shifts: list of Shift objects

        :param show_hidden: list hidden shifts
        :type show_hidden: boolean
        """
        tmp_shifts = dict()

        # no shifts are given -> use all shifts of this job
        if not shifts:
            if show_hidden:
                shifts = self.shift_set.all()
            else:
                shifts = self.shift_set.filter(hidden=False)

        # iterate over all shifts and group them by day
        # (itertools.groupby is strange...)
        for shift in shifts:
            day = localtime(shift.begin).date()

            # add to list
            if day in tmp_shifts:
                tmp_shifts[day].append(shift)
            # or create begin list
            else:
                tmp_shifts[day] = [shift, ]

        # sort days
        ordered_shifts = OrderedDict(sorted(tmp_shifts.items(),
                                     key=lambda t: t[0]))

        # sort shifts
        for day in ordered_shifts:
            ordered_shifts[day] = sorted(ordered_shifts[day],
                                         key=lambda s: s.begin)

        return ordered_shifts

    def duplicate(self, new_event, gift_set_mapping):
        new_job = deepcopy(self)

        new_job.pk = None
        new_job.event = new_event
        new_job.archived_number_coordinators = 0

        # role and design will be updated from BadgeSettings.duplicate
        if self.event.badges:
            new_job.badge_defaults = self.badge_defaults.duplicate()

        new_job.save()

        new_job.job_admins.clear()
        new_job.coordinators.clear()

        for shift in self.shift_set.all():
            shift.duplicate(new_job, gift_set_mapping)

        return new_job


@receiver(pre_save, sender=Job, dispatch_uid='job_pre_save')
def job_pre_save(sender, instance, using, **kwargs):
    """ Add badge defaults if necessary.

    This is a signal handler, that is called, before a job is saved. It
    adds the badge defaults if badge creation is enabled and it is not
    there already.
    """
    if instance.event.badges and not instance.badge_defaults:
        defaults = BadgeDefaults()
        defaults.save()

        instance.badge_defaults = defaults


# moving the import down here fixes a problem with a circular import
from .helper import Helper
