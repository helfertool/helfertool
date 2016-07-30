from django.db import models

class SentMail(models.Model):
    event = models.OneToOneField(
        'registration.Event'
    )

    sender = models.EmailField()

    cc = models.EmailField()

    response_to = models.EmailField()

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
