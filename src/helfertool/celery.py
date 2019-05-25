from __future__ import absolute_import, unicode_literals

import os

from django.conf import settings
from django.core.mail import mail_admins
from django.views.debug import ExceptionReporter

from celery import Celery
from celery.signals import task_failure

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helfertool.settings")

app = Celery('helfertool')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@task_failure.connect
def celery_error_handler(task_id, exception, traceback, einfo, *args, **kwargs):
    if settings.DEBUG:
        return

    mail_subject = "Task exception - {}".format(exception)
    mail_subject = mail_subject.replace("\n", " ")[:250]

    reporter = ExceptionReporter(None, einfo.type, exception, traceback)
    mail_text = reporter.get_traceback_text()

    mail_admins(mail_subject, mail_text)
