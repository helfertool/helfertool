"""
Django settings for Helfertool, if running inside a container
"""

# we want to change some values if we run inside the container
# so, first import all settings, and then overwrite some specific ones
from helfertool.settings import *

# versioning
HELFERTOOL_CONTAINER_VERSION = get_version("/helfertool/container_version")

# directories - ignore helfertool.yaml here
STATIC_ROOT = Path("/helfertool/static")
MEDIA_ROOT = Path("/data/media")
TMP_ROOT = Path("/data/tmp")

# use X-Forwarded-Proto header to determine if https is used
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# always compress static files in container
COMPRESS_OFFLINE = True

# send logs to rsyslog running in container
LOGGING["handlers"]["helfertool_syslog_container"] = {
    "class": "logging.handlers.SysLogHandler",
    "formatter": "helfertool_syslog",
    "level": "INFO",
    "facility": "local7",
    "address": ("localhost", 5140),
}

LOGGING["loggers"]["helfertool"]["handlers"].append("helfertool_syslog_container")
