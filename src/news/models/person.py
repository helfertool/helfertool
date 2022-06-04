from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mail.tracking import new_tracking_news_confirm

from smtplib import SMTPException

import uuid

import logging

logger = logging.getLogger("helfertool.news")


class Person(models.Model):
    """Newsletter recipient.

    Columns:
        :token: Token for confirm/unsubscribe URLs
        :email: Mail address
        :timestamp: Timestamp of initial subscription (creation time of object)
        :validated: Mail address validated (GDPR double opt-in)
        :timestamp_validated: Timestamp of mail validation (GDPR double opt-in)
        :withevent: Subscription during event registration or separately? (for statistics)
    """

    class Meta:
        ordering = [
            "timestamp",
        ]

    token = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        verbose_name=_("E-Mail"),
        unique=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    validated = models.BooleanField(
        default=False,
        verbose_name=_("Validation e-mail was confirmed (double opt-in)"),
    )

    timestamp_validated = models.DateTimeField(
        blank=True,
        null=True,
    )

    withevent = models.BooleanField(
        default=True,
        verbose_name=_("Helper subscribed during registration for event"),
    )

    def __str__(self):
        return self.email

    def send_validation_mail(self, request):
        """Send a validation e-mail to the specified mail address (GDPR double opt-in).

        Used for public newsletter subscription.
        If a helper subscribed during the registration, no separate mail is sent.
        """
        # generate URLs
        domain = request.get_host()
        confirm_url = request.build_absolute_uri(reverse("news:subscribe_confirm", args=[self.token]))

        # generate subject and text from templates
        subject_template = get_template("news/mail/validation_subject.txt")
        subject = subject_template.render().rstrip()

        text_template = get_template("news/mail/validation_text.txt")
        text = text_template.render({"confirm_url": confirm_url, "domain": domain})

        tracking_header = new_tracking_news_confirm(self)

        # sent it and handle errors
        mail = EmailMessage(
            subject,
            text,
            settings.EMAIL_SENDER_ADDRESS,
            [
                self.email,
            ],  # to
            reply_to=[
                settings.EMAIL_SENDER_ADDRESS,
            ],
            headers=tracking_header,
        )

        try:
            mail.send(fail_silently=False)
            return True
        except (SMTPException, ConnectionError) as e:
            logger.error(
                "newsletter mailerror",
                extra={
                    "email": self.email,
                    "error": str(e),
                },
            )

            return False
