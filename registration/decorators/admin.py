from django.contrib.auth.decorators import login_required

from ..views.utils import is_admin, is_involved, nopermission


def admin_required(function):
    @login_required
    def _decorated(request, *args, **kwargs):
        event_url_name = kwargs.get('event_url_name')
        if event_url_name:
            if not is_admin(request.user, event_url_name):
                return nopermission(request)

        return function(request, *args, **kwargs)

    return _decorated


def involvement_required(function):
    @login_required
    def _decorated(request, *args, **kwargs):
        event_url_name = kwargs.get('event_url_name')
        if event_url_name:
            if not is_involved(request.user, event_url_name):
                return nopermission(request)

        return function(request, *args, **kwargs)

    return _decorated
