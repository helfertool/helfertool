from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from registration.permissions import has_access, ACCESS_INVOLVED, ACCESS_MAILS_VIEW, ACCESS_JOB_VIEW_MAILS


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

    tracking_uuid = models.fields.UUIDField(
        null=True,
        blank=True,
    )

    tracking_helper = models.ManyToManyField(
        'registration.Helper',
        through='MailDelivery',
    )

    def __str__(self):
        return "%s - %s" % (self.event, self.subject)

    def can_see_mail(self, user):
        # not involved at all -> no
        if not has_access(user, self.event, ACCESS_INVOLVED):
            return False

        # can view all mails -> yes
        if has_access(user, self.event, ACCESS_MAILS_VIEW):
            return True

        # involved and mail sent to everybody -> yes
        if self.all_helpers_and_coordinators:
            return True

        # mails to all coordinators are only visible for admins

        for job in self.jobs_all.all():
            if has_access(user, job, ACCESS_JOB_VIEW_MAILS):
                return True

        for job in self.jobs_only_coordinators.all():
            if has_access(user, job, ACCESS_JOB_VIEW_MAILS):
                return True

        for shift in self.shifts.all():
            if has_access(user, job, ACCESS_JOB_VIEW_MAILS):
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


class MailDelivery(models.Model):
    helper = models.ForeignKey(
        'registration.Helper',
        on_delete=models.CASCADE,
    )

    sentmail = models.ForeignKey(
        'SentMail',
        on_delete=models.CASCADE,
    )

    failed = models.CharField(
        blank=True,
        null=True,
        default=None,
        max_length=512,
    )

    def __str__(self):
        return "%s - %s" % (self.sentmail, self.helper.email)
