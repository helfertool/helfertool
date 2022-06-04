from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from axes.helpers import get_client_ip_address
from axes.signals import user_locked_out

import logging

logger = logging.getLogger("helfertool.account")


@receiver(user_logged_in)
def user_logged_in_logger(sender, request, user, **kwargs):
    ip_address = get_client_ip_address(request)

    logger.info(
        "login successful",
        extra={
            "user": user,
            "ip": ip_address,
        },
    )


@receiver(user_login_failed)
def user_login_failed_logger(sender, credentials, request, **kwargs):
    ip_address = get_client_ip_address(request)

    logger.warning(
        "login failed",
        extra={
            "user": credentials.get("username", ""),
            "ip": ip_address,
        },
    )


@receiver(user_locked_out)
def user_locked_out_logger(request, username, ip_address, **kwargs):
    logger.warning(
        "user locked",
        extra={
            "user": username,
            "ip": ip_address,
        },
    )
