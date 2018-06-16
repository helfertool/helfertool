from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class SentMail(models.Model):
    class Meta:
        ordering = ['-date', ]

    event = models.ForeignKey(
        'registration.Event',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )

    sender = models.EmailField()

    cc = models.EmailField(
        blank=True,
    )

    reply_to = models.EmailField(
        blank=True,
    )

    subject = models.CharField(
        max_length=200,
    )

    text = models.TextField()

    all_helpers_and_coordinators = models.BooleanField(
        default=False,
    )

    all_coordinators = models.BooleanField(
        default=False,
    )

    jobs_all = models.ManyToManyField(
        'registration.Job',
        related_name='sent_mails_all',
        blank=True,
    )

    jobs_only_coordinators = models.ManyToManyField(
        'registration.Job',
        related_name='sent_mails_only_coordinators',
        blank=True,
    )

    shifts = models.ManyToManyField(
        'registration.Shift',
        blank=True,
    )

    failed = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return "%s - %s - %s" % (self.event, self.user, self.date)

    def can_see_mail(self, user):
        if not self.event.is_involved(user):
            return False

        if self.event.is_admin(user):
            return True

        if self.all_helpers_and_coordinators:
            return True

        # mails to all coordinators are only visible for admins

        for job in self.jobs_all.all():
            if job.is_admin(user):
                return True

        for job in self.jobs_only_coordinators.all():
            if job.is_admin(user):
                return True

        for shift in self.shifts.all():
            if shift.job.is_admin(user):
                return True

        return False

    @property
    def receiver_list(self):
        tmp = []

        if self.all_helpers_and_coordinators:
            tmp.append(_("All helpers and coordinators"))
            return tmp

        if self.all_coordinators:
            tmp.append(_("All coordinators"))

        for job in self.jobs_all.all():
            tmp.append(_("{}, Helpers and coordinators").format(job.name))

        for job in self.jobs_only_coordinators.all():
            tmp.append(_("{}, Coordinators").format(job.name))

        for shift in self.shifts.all():
            tmp.append(str(shift))

        return tmp
