from __future__ import absolute_import

from celery import task
from celery.five import monotonic
from contextlib import contextmanager
from django.conf import settings
from django.core.cache import caches

from .receive import MailHandler

LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


@contextmanager
def cache_lock(lock_id, oid):
    # source: https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html
    # we use the database cache backend here, this is not as good as using memcached,
    # but should be good enough for the use case
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = caches['locks'].add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            caches['locks'].delete(lock_id)


@task(bind=True)
def receive_mails(self):
    if settings.RECEIVE_EMAIL_HOST:
        with cache_lock("receive_mails", self.app.oid) as acquired:
            if acquired:
                handler = MailHandler()
                handler.run(do_forward=settings.FORWARD_UNHANDLED_ADDRESS is not None)
