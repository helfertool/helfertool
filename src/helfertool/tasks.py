from __future__ import absolute_import

from celery.signals import task_failure

from django.conf import settings
from django.core.mail import mail_admins
from django.views.debug import ExceptionReporter


@task_failure.connect
def celery_error_handler(task_id, exception, traceback, einfo, *args, **kwargs):
    if settings.DEBUG:
        return

    mail_subject = "Task exception - {}".format(exception)
    mail_subject = mail_subject.replace("\n", " ")[:250]

    reporter = ExceptionReporter(None, einfo.type, exception, traceback)
    mail_text = reporter.get_traceback_text()

    mail_admins(mail_subject, mail_text)
