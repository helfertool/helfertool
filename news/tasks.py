from __future__ import absolute_import

from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation

from celery import shared_task

from .models import Person


@shared_task
def send_news_mails(first_language, append_english, subject, text, text_en,
                    url, unsubsribe_url):
        prev_language = translation.get_language()

        mails = []
        for person in Person.objects.all():
            text = ""
            tmp_unsubscribe_url = unsubsribe_url.replace("EMAIL", person.email)

            if append_english:
                text += render_to_string("news/mail/english.txt")

            text += _mail_text_language(first_language, text, url,
                                        tmp_unsubscribe_url)

            if append_english:
                text += _mail_text_language("en", text_en, url,
                                            tmp_unsubscribe_url)

            text = text.lstrip().rstrip()

            mails.append((subject, text, settings.FROM_MAIL, [person.email]))

        translation.activate(prev_language)

        # send mails
        send_mass_mail(mails)


def _mail_text_language(language, text, url, unsubscribe_url):
    translation.activate(language)

    tmp = ""
    tmp += render_to_string("news/mail/preface.txt", {'url': url})
    tmp += text
    tmp += render_to_string("news/mail/end.txt",
                            {'unsubscribe_url': unsubscribe_url})

    return tmp
