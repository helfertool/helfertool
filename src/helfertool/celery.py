from __future__ import absolute_import, unicode_literals

import os

from django.conf import settings
from django.core.mail import mail_admins
from django.views.debug import ExceptionReporter

from celery import Celery
from celery.signals import task_failure

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helfertool.settings")

# init celery
app = Celery("helfertool")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # note: exceptions in this code are not displayed in celery
    # for debugging, add own exception handling that prints all exceptions
    #
    # additionally, django is not fully loaded here. importing models will fail
    from mail.tasks import receive_mails

    sender.add_periodic_task(settings.RECEIVE_INTERVAL, receive_mails.s())

    from news.tasks import cleanup

    sender.add_periodic_task(3600, cleanup.s())


@task_failure.connect
def celery_error_handler(task_id, exception, traceback, einfo, *args, **kwargs):
    if settings.DEBUG:
        return

    mail_subject = "Task exception - {}".format(exception)
    mail_subject = mail_subject.replace("\n", " ")[:250]

    reporter = ExceptionReporter(None, einfo.type, exception, traceback)
    mail_text = reporter.get_traceback_text()

    mail_admins(mail_subject, mail_text)
