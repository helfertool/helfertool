from __future__ import absolute_import

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation

from celery import shared_task

import smtplib
import time

from .models import Person


@shared_task
def send_news_mails(first_language, append_english, subject, text, text_en,
                    unsubsribe_url):
        prev_language = translation.get_language()

        count = 0
        for person in Person.objects.all():
            # build mail text
            mail_text = ""
            tmp_unsubscribe_url = unsubsribe_url + str(person.token)

            if append_english:
                mail_text += render_to_string("news/mail/english.txt")

            mail_text += _mail_text_language(first_language, text,
                                             tmp_unsubscribe_url)

            if append_english:
                mail_text += _mail_text_language("en", text_en,
                                                 tmp_unsubscribe_url)

            mail_text = mail_text.lstrip().rstrip()

            # send mail
            try:
                send_mail(subject, mail_text, settings.DEFAULT_FROM_MAIL, [person.email])
            except smtplib.SMTPRecipientsRefused:
                pass

            count += 1

            # wait a bit after a batch of mails
            if count >= settings.MAIL_BATCH_SIZE:
                count = 0
                time.sleep(settings.MAIL_BATCH_GAP)

        translation.activate(prev_language)


def _mail_text_language(language, text, unsubscribe_url):
    translation.activate(language)

    tmp = ""
    tmp += render_to_string("news/mail/preface.txt")
    tmp += text
    tmp += render_to_string("news/mail/end.txt",
                            {'unsubscribe_url': unsubscribe_url})

    return tmp
