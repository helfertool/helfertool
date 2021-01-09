from __future__ import absolute_import

from celery import task
from django.conf import settings

from helfertool.utils import cache_lock
from .receive import MailHandler


@task(bind=True)
def receive_mails(self):
    if settings.RECEIVE_EMAIL_HOST:
        with cache_lock("receive_mails", self.app.oid) as acquired:
            if acquired:
                handler = MailHandler()
                handler.run(do_forward=settings.FORWARD_UNHANDLED_ADDRESS is not None)
