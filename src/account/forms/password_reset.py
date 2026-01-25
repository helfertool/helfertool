from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import EmailMessage
from django.template.loader import get_template

from axes.helpers import get_client_ip_address

from captcha.fields import CaptchaField
from helfertool.forms import CustomCaptchaTextInput

import logging

logger = logging.getLogger("helfertool.account")


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

        if not settings.CAPTCHAS_PASSWORD_RESET:
            self.fields.pop("captcha")

    def save(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).save(*args, **kwargs)

        # log password reset attempt
        email = self.cleaned_data["email"]
        ip_address = get_client_ip_address(kwargs.get("request"))
        logger.info(
            "password resetattempt",
            extra={
                "email": email,
                "ip": ip_address,
            },
        )

    captcha = CaptchaField(widget=CustomCaptchaTextInput)


class CustomSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        user = super(CustomSetPasswordForm, self).save(commit)

        # log password reset
        logger.info(
            "password reset",
            extra={
                "changed_user": user.username,
            },
        )

        # sent confirmation mail to user
        context = {
            "firstname": user.first_name,
            "page_title": settings.PAGE_TITLE,
            "contact_mail": settings.CONTACT_MAIL,
        }
        subject_template = get_template("account/password_reset/completed_mail_subject.txt")
        subject = subject_template.render(context).strip()

        text_template = get_template("account/password_reset/completed_mail.txt")
        text = text_template.render(context)

        # sent it and handle errors
        mail = EmailMessage(
            subject,
            text,
            settings.EMAIL_SENDER_ADDRESS,
            [user.email],  # to
            reply_to=[settings.EMAIL_SENDER_ADDRESS],
        )

        mail.send(fail_silently=True)

        return user
