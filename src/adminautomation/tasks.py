from __future__ import absolute_import

from celery import shared_task
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from datetime import timedelta

from .utils import event_archive_automation_enabled

from helfertool.utils import cache_lock


@shared_task(bind=True)
def event_archive_automation(self):
    from .models import EventArchiveAutomation
    from registration.models import Event

    if not event_archive_automation_enabled():
        return

    with cache_lock("event_archive_automation", self.app.oid) as acquired:
        if acquired:
            today = timezone.now().date()

            # get all events that are not archived, but should be (soon)
            deadline = (
                today
                - relativedelta(months=settings.AUTOMATION_EVENTS_ARCHIVE_DEADLINE)
                + relativedelta(day=settings.AUTOMATION_EVENTS_ARCHIVE_START_BEFORE_DEADLINE)
            )
            events = Event.objects.filter(archived=False, date__lte=deadline)

            for event in events:
                automation_data, created = EventArchiveAutomation.objects.get_or_create(event=event)

                # there is an exception and it is not reached yet -> skip
                if automation_data.exception_date and automation_data.exception_date >= today:
                    continue

                # a reminder was sent within the specified interval -> skip
                if automation_data.last_reminder is not None and (today - automation_data.last_reminder) < timedelta(
                    days=settings.AUTOMATION_EVENTS_ARCHIVE_INTERVAL
                ):
                    continue

                # send mail
                subject_template = get_template("adminautomation/mail/event_archive_automation_subject.txt")
                subject = subject_template.render(
                    {
                        "event": event,
                        "page_title": settings.PAGE_TITLE,
                    }
                ).rstrip()

                text_template = get_template("adminautomation/mail/event_archive_automation.txt")
                text = text_template.render(
                    {
                        "event": event,
                        "docs": settings.AUTOMATION_EVENTS_ARCHIVE_DOCS,
                    }
                )

                mail_sent = event.send_admin_mail(subject, text)

                # update timestamps
                if mail_sent:
                    automation_data.last_reminder = today
                    automation_data.save()
