from __future__ import absolute_import

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation, timezone

from celery import task, shared_task

from mail.tracking import new_tracking_news

import smtplib
import time

from dateutil.relativedelta import relativedelta


@shared_task
def send_news_mails(first_language, append_english, subject, text, text_en, unsubsribe_url):
    # import on top would break setup_periodic_tasks in helfertool/celery.py as django is not fully loaded
    # so we import it here
    from news.models import Person

    prev_language = translation.get_language()

    count = 0
    for person in Person.objects.filter(validated=True):
        # build mail text
        mail_text = ""
        tmp_unsubscribe_url = unsubsribe_url + str(person.token)

        if append_english:
            mail_text += render_to_string("news/mail/newsletter_english.txt")

        mail_text += _mail_text_language(first_language, text, tmp_unsubscribe_url)

        if append_english:
            mail_text += _mail_text_language("en", text_en, tmp_unsubscribe_url)

        mail_text = mail_text.lstrip().rstrip()

        tracking_header = new_tracking_news(person)

        # send mail
        try:
            mail = EmailMessage(subject,
                                mail_text,
                                settings.EMAIL_SENDER_ADDRESS,
                                [person.email, ],
                                headers=tracking_header)
            mail.send(fail_silently=False)
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
    tmp += render_to_string("news/mail/newsletter_preface.txt")
    tmp += text
    tmp += render_to_string("news/mail/newsletter_end.txt",
                            {'unsubscribe_url': unsubscribe_url})

    return tmp


@task
def cleanup():
    """ Delete newsletter subscriptions that were not validated for some time (3 days by default).

    This tasks is executed every hour via celery beat.
    """
    # import on top would break setup_periodic_tasks in helfertool/celery.py as django is not fully loaded
    # so we import it here
    from news.models import Person

    deadline = timezone.now() - relativedelta(days=settings.NEWS_SUBSCRIBE_DEADLINE)
    Person.objects.filter(validated=False, timestamp__lte=deadline).delete()
