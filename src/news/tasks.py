from __future__ import absolute_import

from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation

from celery import shared_task

import time

from .models import Person


@shared_task
def send_news_mails(first_language, append_english, subject, text, text_en,
                    url, unsubsribe_url):
        prev_language = translation.get_language()

        mails = []
        for person in Person.objects.all():
            mail_text = ""
            tmp_unsubscribe_url = unsubsribe_url + str(person.token)

            if append_english:
                mail_text += render_to_string("news/mail/english.txt")

            mail_text += _mail_text_language(first_language, text, url,
                                             tmp_unsubscribe_url)

            if append_english:
                mail_text += _mail_text_language("en", text_en, url,
                                                 tmp_unsubscribe_url)

            mail_text = mail_text.lstrip().rstrip()

            mails.append((subject, mail_text, settings.DEFAULT_FROM_MAIL,
                          [person.email]))

        translation.activate(prev_language)

        # send mails
        batch = 0
        while True:
            mails_batch = mails[batch*settings.MAIL_BATCH_SIZE:
                                (batch+1)*settings.MAIL_BATCH_SIZE]
            if not mails_batch:
                break

            send_mass_mail(mails_batch)
            time.sleep(settings.MAIL_BATCH_GAP)
            batch += 1


def _mail_text_language(language, text, url, unsubscribe_url):
    translation.activate(language)

    tmp = ""
    tmp += render_to_string("news/mail/preface.txt", {'url': url})
    tmp += text
    tmp += render_to_string("news/mail/end.txt",
                            {'unsubscribe_url': unsubscribe_url})

    return tmp
