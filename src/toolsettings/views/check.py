from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.shortcuts import render

import kombu
import ldap

from registration.views.utils import nopermission

from ..models import HTMLSetting, TextSetting


@login_required
def check(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # templates
    templates_ok = True

    for html_setting in ('about', 'privacy', 'privacy_newsletter', 'login', 'add_user'):
        try:
            HTMLSetting.objects.get(key=html_setting)
        except HTMLSetting.DoesNotExist:
            templates_ok = False

    for text_setting in ('privacy', ):
        try:
            TextSetting.objects.get(key=text_setting)
        except TextSetting.DoesNotExist:
            templates_ok = False

    # mail
    mail_ok = True
    try:
        mail_conn = mail.get_connection()
        if isinstance(mail_conn, EmailBackend):
            mail_conn.open()
    except (ConnectionRefusedError, OSError):
        mail_ok = False

    # celery
    celery_broker_ok = True
    try:
        celery_conn = kombu.Connection(settings.CELERY_BROKER_URL)
        celery_conn.ensure_connection(max_retries=1)
    except kombu.exceptions.OperationalError:
        celery_broker_ok = False

    # ldap
    if 'django_auth_ldap.backend.LDAPBackend' in settings.AUTHENTICATION_BACKENDS:
        ldap_configured = True
        ldap_ok = True
        try:
            ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN,
                                    settings.AUTH_LDAP_BIND_PASSWORD)
        except ldap.LDAPError:  # pylint: disable=E1101
            ldap_ok = False
    else:
        ldap_configured = False
        ldap_ok = False

    # headers
    header_host = request.META.get('HTTP_HOST')
    header_remote_addr = request.META.get('REMOTE_ADDR')
    header_x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    header_x_forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO')

    context = {
        'version': settings.HELFERTOOL_VERSION,
        'container_version': settings.HELFERTOOL_CONTAINER_VERSION,
        'similarity_search': not settings.SEARCH_SIMILARITY_DISABLED,

        'templates_ok': templates_ok,
        'mail_ok': mail_ok,
        'celery_broker_ok': celery_broker_ok,
        'ldap_configured': ldap_configured,
        'ldap_ok': ldap_ok,

        'header_host': header_host,
        'header_remote_addr': header_remote_addr,
        'header_x_forwarded_for': header_x_forwarded_for,
        'header_x_forwarded_proto': header_x_forwarded_proto,
    }
    return render(request, 'toolsettings/check.html', context)
