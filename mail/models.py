from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class SentMail(models.Model):
    event = models.ForeignKey(
        'registration.Event'
    )

    user = models.ForeignKey(
        User,
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )

    sender = models.EmailField()

    cc = models.EmailField(
        blank=True,
    )

    response_to = models.EmailField(
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
