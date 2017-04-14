from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import posixpath

from .. import tasks


def _badge_upload_path(instance, filename):
    event = str(instance.helper.event.pk)

    return posixpath.join('badges', event, 'photos', filename)


class Badge(models.Model):
    helper = models.OneToOneField(
        'registration.Helper',
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

    def save(self, *args, **kwargs):
        super(Badge, self).save(*args, **kwargs)

        if self._old_photo != self.photo and self.photo:
            tasks.scale_badge_photo.delay(self.photo.path)

    def get_job(self):
        # use primary job if set
        if self.primary_job:
            return self.primary_job

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

    def _get_defaults(self, key):
        job = self.get_job()

        # job ambiguous -> event default
        if not job:
            return getattr(self.helper.event.badge_settings.defaults, key)

        # try if 'key' is set for selected job
        if getattr(job.badge_defaults, key):
            return getattr(job.badge_defaults, key)

        # else use event's default
        return getattr(self.helper.event.badge_settings.defaults, key)

    def is_ambiguous(self):
        return self.get_job() is None

    def get_design(self):
        return self.custom_design or self._get_defaults('design')

    def get_role(self):
        return self.custom_role or self._get_defaults('role')

    def no_default_role(self):
        return self._get_defaults('no_default_role')
