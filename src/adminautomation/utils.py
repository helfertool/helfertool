from django.conf import settings


def event_archive_automation_enabled():
    return (
        settings.AUTOMATION_EVENTS_ARCHIVE_DEADLINE is not None
        and settings.AUTOMATION_EVENTS_ARCHIVE_INTERVAL is not None
    )
