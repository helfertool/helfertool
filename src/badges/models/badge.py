from django.db import models
from django.template.defaultfilters import date as date_f
from django.utils.translation import ugettext_lazy as _

import posixpath

from .. import tasks
from .settings import BadgeSettings


def _badge_upload_path(instance, filename):
    event = str(instance.event.pk)

    return posixpath.join('badges', event, 'photos', filename)


class Badge(models.Model):
    event = models.ForeignKey(
        'registration.Event',
        on_delete=models.CASCADE,
    )

    helper = models.OneToOneField(
        'registration.Helper',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    barcode = models.PositiveIntegerField(
        verbose_name=_("Barcode"),
        null=True,  # will be set in save method
        blank=True,
    )

    firstname = models.CharField(
        max_length=200,
        verbose_name=_("Other firstname"),
        blank=True,
    )

    surname = models.CharField(
        max_length=200,
        verbose_name=_("Other surname"),
        blank=True,
    )

    job = models.CharField(
        max_length=200,
        verbose_name=_("Other text for job"),
        blank=True,
    )

    shift = models.CharField(
        max_length=200,
        verbose_name=_("Other text for shift"),
        blank=True,
    )

    role = models.CharField(
        max_length=200,
        verbose_name=_("Other text for role"),
        blank=True,
    )

    photo = models.ImageField(
        verbose_name=_("Photo"),
        upload_to=_badge_upload_path,
        blank=True,
        null=True,
    )

    primary_job = models.ForeignKey(
        'registration.Job',
        verbose_name=_("Primary job"),
        help_text=_("Only necessary if this person has multiple jobs."),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    custom_role = models.ForeignKey(
        'BadgeRole',
        related_name='+',  # no reverse accessor
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Role"),
    )

    custom_design = models.ForeignKey(
        'BadgeDesign',
        related_name='+',  # no reverse accessor
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Design"),
    )

    printed = models.BooleanField(
        default=False,
        verbose_name=_("Badge was printed already"),
    )

    def __init__(self, *args, **kwargs):
        super(Badge, self).__init__(*args, **kwargs)

        self._old_photo = self.photo

    def __str__(self):
        return "{} - {}".format(self.event, self.name())

    def save(self, *args, **kwargs):
        super(Badge, self).save(*args, **kwargs)

        if not self.barcode:
            self.barcode = self.pk
            self.save()

        if self._old_photo != self.photo and self.photo:
            # pylint: disable=no-member
            tasks.scale_badge_photo.delay(self.photo.path)
            self._old_photo = self.photo  # do not run task multiple times

    def name(self):
        """ The name of the badge (for messages in web interface) """
        if self.helper:
            return self.helper.full_name
        else:
            return "{} {}".format(self.firstname, self.surname)

    def get_job(self):
        """ Get the job to which the badge belongs.

        If a primary job is selected, that's it.
        If the helper is coordinator for exactle one job, that's it.

        Otherwise, we cannot decide.
        """
        # use primary job if set
        if self.primary_job:
            return self.primary_job

        # it's a special badge without helper -> we don't care and abort
        if not self.helper:
            return None

        # check if is coordinator
        coordinated_jobs = self.helper.coordinated_jobs
        if len(coordinated_jobs) == 1:
            return coordinated_jobs[0]
        elif len(coordinated_jobs) > 1:
            return None

        # collect all jobs
        jobs = []

        for shift in self.helper.shifts.all():
            if shift.job not in jobs:
                jobs.append(shift.job)

        # only one job -> done
        if len(jobs) == 1:
            return jobs[0]

        return None

    def is_ambiguous(self):
        return self.get_job() is None

    def _get_defaults(self, key):
        job = self.get_job()

        # job ambiguous -> event default
        if not job:
            return getattr(self.event.badge_settings.defaults, key)

        # try if 'key' is set for selected job
        if getattr(job.badge_defaults, key):
            return getattr(job.badge_defaults, key)

        # else use event's default
        return getattr(self.event.badge_settings.defaults, key)

    def get_design(self):
        return self.custom_design or self._get_defaults('design')

    def get_role(self):
        return self.custom_role or self._get_defaults('role')

    def no_default_role(self):
        return self._get_defaults('no_default_role')

    def get_firstname_text(self):
        """ Return text for surname on badge """
        return self.firstname or (self.helper.firstname if self.helper else "")

    def get_surname_text(self):
        """ Return text for surname on badge """
        return self.surname or (self.helper.surname if self.helper else "")

    def get_job_text(self):
        """ Return text for job on badge """
        if self.job:
            return self.job
        else:
            job = self.get_job()  # get the primary job
            if job:
                return job.name
        return ""

    def get_shift_text(self, badgesettings):
        """ Return text for shift on badge """
        if self.shift:
            return self.shift
        elif self.helper:
            return self._get_auto_shift_text(self.helper, self.get_job(), badgesettings)
        return ""

    def get_role_text(self, badgesettings):
        """ Return text for role on badge """
        if self.role:
            return self.role
        elif self.helper and not self.no_default_role():
            # no_default_role means that we do not want to have a role like "coordinator" on the badge
            if self.helper.is_coordinator:
                return badgesettings.coordinator_title
            else:
                return badgesettings.helper_title
        return ""

    def _get_auto_shift_text(self, helper, primary_job, badgesettings):
        """
        We create a string like: Shift 1, Shift 2 (Other job), Shift 3
        Depending on the settings, we use the shift name (if available) or the time in a certain format.
        The job is added if it is not the primary job.

        Returns the text (not LaTeX escaped!)
        """
        shift_texts = []
        for shift in helper.shifts.all().order_by('begin'):
            # get shift date / name
            cur_text = ""
            if not badgesettings.shift_no_names and shift.name:
                # we want to use a name and have one
                cur_text = shift.name
            else:
                # use time. format depends on settings, but we always needs the time
                cur_text = shift.time_hours()

                # the date format depends on the settings
                date_format_string = None
                if badgesettings.shift_format == BadgeSettings.SHIFT_FORMAT_DATE:
                    date_format_string = "d.m"
                elif badgesettings.shift_format == BadgeSettings.SHIFT_FORMAT_WEEKDAY:
                    date_format_string = "D"

                # add the date, if we want to
                if date_format_string:
                    cur_text = "{} {}".format(date_f(shift.date(), date_format_string), cur_text)

            # add job if it is not the primary job
            if shift.job != primary_job:
                cur_text = "{} ({})".format(cur_text, shift.job.name)

            shift_texts.append(cur_text)

        return ', '.join(shift_texts)
