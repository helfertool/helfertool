from django import template
from django.utils.timesince import timesince
from django.utils.timezone import is_aware
from django.utils.translation import gettext_lazy as _

import datetime


register = template.Library()


@register.filter
def lastlogin(user):
    if not user.last_login:
        return _("Never")

    login_date = _to_date(user.last_login)
    now_date = _to_date(datetime.datetime.now(datetime.timezone.utc if is_aware(login_date) else None))

    if login_date == now_date:
        return _("Today")
    elif login_date == now_date - datetime.timedelta(days=1):
        return _("Yesterday")
    else:
        last_login_ago = timesince(login_date, now_date)
        return _("%(last_login_ago)s ago") % {"last_login_ago": last_login_ago}


def _to_date(timestamp):
    return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
