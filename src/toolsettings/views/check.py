from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.mail.backends.smtp import EmailBackend
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission
from mail.receive.error import MailHandlerError
from mail.receive.receiver import MailReceiver

from ..models import HTMLSetting, TextSetting

import kombu
import ldap
import socket


@login_required
@never_cache
def check(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # weak secret key
    secret_ok = True
    if settings.SECRET_KEY in ["change_this_for_production", "CHANGEME"]:
        secret_ok = False
    if len(settings.SECRET_KEY) < 50:
        secret_ok = False

    # templates
    templates_ok = True

    for html_setting in ("about", "privacy", "privacy_newsletter", "login", "add_user", "newsletter"):
        try:
            HTMLSetting.objects.get(key=html_setting)
        except HTMLSetting.DoesNotExist:
            templates_ok = False

    for text_setting in ("privacy",):
        try:
            TextSetting.objects.get(key=text_setting)
        except TextSetting.DoesNotExist:
            templates_ok = False

    # mail (smtp)
    mail_smtp_ok = True
    try:
        mail_conn = mail.get_connection()
        if isinstance(mail_conn, EmailBackend):
            mail_conn.open()
    except (ConnectionRefusedError, OSError, socket.gaierror):
        mail_smtp_ok = False

    # mail (imap)
    if settings.RECEIVE_EMAIL_HOST:
        mail_imap_configured = True
        try:
            receiver = MailReceiver()
            receiver.connect()
            receiver.close()

            mail_imap_ok = True
        except MailHandlerError:
            mail_imap_ok = False
    else:
        mail_imap_configured = False
        mail_imap_ok = False

    # celery
    celery_broker_ok = True
    try:
        celery_conn = kombu.Connection(settings.CELERY_BROKER_URL)
        celery_conn.ensure_connection(max_retries=1)
    except kombu.exceptions.OperationalError:
        celery_broker_ok = False

    # ldap
    if "django_auth_ldap.backend.LDAPBackend" in settings.AUTHENTICATION_BACKENDS:
        ldap_configured = True
        ldap_ok = True
        try:
            ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        except ldap.LDAPError:  # pylint: disable=E1101
            ldap_ok = False
    else:
        ldap_configured = False
        ldap_ok = False

    # headers
    header_host = request.headers.get("host")
    header_x_forwarded_for = request.headers.get("x-forwarded-for")
    header_x_forwarded_proto = request.headers.get("x-forwarded-proto")

    context = {
        "version": settings.HELFERTOOL_VERSION,
        "container_version": settings.HELFERTOOL_CONTAINER_VERSION,
        "debug": settings.DEBUG,
        "similarity_search": not settings.SEARCH_SIMILARITY_DISABLED,
        "secret_ok": secret_ok,
        "templates_ok": templates_ok,
        "mail_smtp_ok": mail_smtp_ok,
        "mail_imap_configured": mail_imap_configured,
        "mail_imap_ok": mail_imap_ok,
        "celery_broker_ok": celery_broker_ok,
        "ldap_configured": ldap_configured,
        "ldap_ok": ldap_ok,
        "header_host": header_host,
        "header_x_forwarded_for": header_x_forwarded_for,
        "header_x_forwarded_proto": header_x_forwarded_proto,
    }
    return render(request, "toolsettings/check.html", context)
