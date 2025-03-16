"""
Django settings for Helfertool.
"""

import os
import socket
import sys
import yaml

from django.utils.translation import gettext_lazy as _

from datetime import timedelta
from pathlib import Path

from .utils import dict_get, build_path, get_version, pg_trgm_installed

# import josepy, otherwise the oidc module does not work properly...
import josepy

BASE_DIR = Path(__file__).resolve().parent.parent

# import configuration file
config_file = os.environ.get("HELFERTOOL_CONFIG_FILE", BASE_DIR / "helfertool.yaml")

try:
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
except FileNotFoundError:
    print("Configuration file not found: {}".format(config_file))
    sys.exit(1)
except IOError:
    print("Cannot read configuration file: {}".format(config_file))
    sys.exit(1)
except yaml.parser.ParserError as e:
    print("Syntax error in configuration file:")
    print()
    print(e)
    sys.exit(1)

# versioning
HELFERTOOL_VERSION = get_version(BASE_DIR / "version.txt")
HELFERTOOL_CONTAINER_VERSION = None  # will be set in settings_container.py

# directories for static and media files (overwritten in settings_container.py)
STATIC_ROOT = build_path(dict_get(config, "static", "files", "static"), BASE_DIR)
MEDIA_ROOT = build_path(dict_get(config, "media", "files", "media"), BASE_DIR)

# directory for temporary files like badges, file uploads (overwritten in settings_container.py)
TMP_ROOT = build_path(dict_get(config, "/tmp", "files", "tmp"), BASE_DIR)

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# file permissions for newly uploaded files and directories
FILE_UPLOAD_PERMISSIONS = 0o640
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o750
FILE_UPLOAD_TEMP_DIR = TMP_ROOT

# internationalization
LANGUAGE_CODE = dict_get(config, "de", "language", "default")

TIME_ZONE = dict_get(config, "Europe/Berlin", "language", "timezone")

LANGUAGE_SINGLELANGUAGE = dict_get(config, False, "language", "singlelanguage")

if LANGUAGE_SINGLELANGUAGE:
    if LANGUAGE_CODE == "de":
        LANGUAGES = (("de", _("German")),)
    elif LANGUAGE_CODE == "en":
        LANGUAGES = (("en", _("English")),)
    else:
        print("Invalid language: {}".format(LANGUAGE_CODE))
        sys.exit(1)
else:
    LANGUAGES = (
        ("de", _("German")),
        ("en", _("English")),
    )

USE_I18N = True
USE_TZ = True

DEFAULT_COUNTRY = dict_get(config, "DE", "language", "country")

# database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends." + dict_get(config, "sqlite3", "database", "backend"),
        "NAME": dict_get(config, "db.sqlite3", "database", "name"),
        "USER": dict_get(config, None, "database", "user"),
        "PASSWORD": dict_get(config, None, "database", "password"),
        "HOST": dict_get(config, None, "database", "host"),
        "PORT": dict_get(config, None, "database", "port"),
        "OPTIONS": dict_get(config, {}, "database", "options"),
    }
}

# build correct relative path for sqlite (if necessary)
if "sqlite3" in DATABASES["default"]["ENGINE"]:
    DATABASES["default"]["NAME"] = build_path(DATABASES["default"]["NAME"], BASE_DIR)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# rabbitmq
CELERY_BROKER_URL = "amqp://{}:{}@{}:{}/{}".format(
    dict_get(config, "guest", "rabbitmq", "user"),
    dict_get(config, "guest", "rabbitmq", "password"),
    dict_get(config, "localhost", "rabbitmq", "host"),
    dict_get(config, "5672", "rabbitmq", "port"),
    dict_get(config, "", "rabbitmq", "vhost"),
)
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_BROKER_POOL_LIMIT = None
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# caches
CACHES = {
    # default cache - not used on purpose currently
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    # select2 needs its own cache
    "select2": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "select2_cache",
    },
    # cache for locks (used by celery tasks to prevent parallel execution)
    "locks": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "locks_cache",
    },
}

# mail
if dict_get(config, None, "mail", "host") is None:
    # new config format: sending and receiving mails separated

    # send
    EMAIL_HOST = dict_get(config, "localhost", "mail", "send", "host")
    EMAIL_PORT = dict_get(config, 25, "mail", "send", "port")
    EMAIL_HOST_USER = dict_get(config, None, "mail", "send", "user")
    EMAIL_HOST_PASSWORD = dict_get(config, None, "mail", "send", "password")
    EMAIL_USE_SSL = dict_get(config, False, "mail", "send", "tls")
    EMAIL_USE_TLS = dict_get(config, False, "mail", "send", "starttls")

    if EMAIL_USE_SSL and EMAIL_USE_TLS:
        print("Mail settings for sending invalid: TLS and STARTTLS are mutually exclusive")
        sys.exit(1)

    # receive
    RECEIVE_EMAIL_HOST = dict_get(config, None, "mail", "receive", "host")
    RECEIVE_EMAIL_PORT = dict_get(config, None, "mail", "receive", "port")
    RECEIVE_EMAIL_HOST_USER = dict_get(config, None, "mail", "receive", "user")
    RECEIVE_EMAIL_HOST_PASSWORD = dict_get(config, None, "mail", "receive", "password")
    RECEIVE_EMAIL_USE_SSL = dict_get(config, False, "mail", "receive", "tls")
    RECEIVE_EMAIL_USE_TLS = dict_get(config, False, "mail", "receive", "starttls")

    RECEIVE_EMAIL_FOLDER = dict_get(config, "INBOX", "mail", "receive", "folder")
    RECEIVE_INTERVAL = dict_get(config, 300, "mail", "receive", "interval")

    if RECEIVE_EMAIL_USE_SSL and RECEIVE_EMAIL_USE_TLS:
        print("Mail settings for receiving invalid: TLS and STARTTLS are mutually exclusive")
        sys.exit(1)
else:
    # old config format
    EMAIL_HOST = dict_get(config, "localhost", "mail", "host")
    EMAIL_PORT = dict_get(config, 25, "mail", "port")
    EMAIL_HOST_USER = dict_get(config, None, "mail", "user")
    EMAIL_HOST_PASSWORD = dict_get(config, None, "mail", "password")
    EMAIL_USE_TLS = dict_get(config, False, "mail", "tls")

# sender of all mails (because of SPF, DKIM, DMARC)
# the display name defaults to the mail address
EMAIL_SENDER_ADDRESS = dict_get(config, "helfertool@localhost", "mail", "sender_address")
EMAIL_SENDER_NAME = dict_get(config, EMAIL_SENDER_ADDRESS, "mail", "sender_name")

SERVER_EMAIL = EMAIL_SENDER_ADDRESS  # for error messages

# forward mails that were not handled automatically to this address
# the display name defaults to the mail address
FORWARD_UNHANDLED_ADDRESS = dict_get(config, None, "mail", "forward_unhandled_address")
FORWARD_UNHANDLED_NAME = dict_get(config, FORWARD_UNHANDLED_ADDRESS, "mail", "forward_unhandled_name")

# newsletter: number of mails sent during one connection and time between
MAIL_BATCH_SIZE = dict_get(config, 200, "mail", "batch_size")
MAIL_BATCH_GAP = dict_get(config, 5, "mail", "batch_gap")

# authentication
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/manage/account/check/"
LOGOUT_REDIRECT_URL = "/"

LOCAL_USER_CHAR = dict_get(config, None, "authentication", "local_user_char")

# LDAP
ldap_config = dict_get(config, None, "authentication", "ldap")
if ldap_config:
    import django_auth_ldap.config
    import ldap

    # server address and authentication
    AUTH_LDAP_SERVER_URI = dict_get(ldap_config, "ldaps://localhost", "server", "host")
    AUTH_LDAP_BIND_DN = dict_get(ldap_config, None, "server", "bind_dn")
    AUTH_LDAP_BIND_PASSWORD = dict_get(ldap_config, None, "server", "bind_password")

    # user search
    user_search_base = dict_get(ldap_config, None, "schema", "user_search_base")
    user_search_filter = dict_get(ldap_config, None, "schema", "user_search_filter")
    if user_search_base is not None and user_search_filter is not None:
        AUTH_LDAP_USER_SEARCH = django_auth_ldap.config.LDAPSearch(
            user_search_base,
            ldap.SCOPE_SUBTREE,  # pylint: disable=E1101
            user_search_filter,
        )

    AUTH_LDAP_USER_DN_TEMPLATE = dict_get(ldap_config, None, "schema", "user_dn_template")

    # user schema
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": dict_get(ldap_config, "givenName", "schema", "first_name_attr"),
        "last_name": dict_get(ldap_config, "sn", "schema", "last_name_attr"),
        "email": dict_get(ldap_config, "mail", "schema", "email_attr"),
    }

    # group schema
    group_type_name = dict_get(ldap_config, "GroupOfNamesType", "schema", "group_type")
    AUTH_LDAP_GROUP_TYPE = getattr(django_auth_ldap.config, group_type_name)()

    AUTH_LDAP_GROUP_SEARCH = django_auth_ldap.config.LDAPSearch(
        dict_get(ldap_config, None, "schema", "group_base_dn"),
        ldap.SCOPE_SUBTREE,  # pylint: disable=E1101
        "(objectClass={})".format(dict_get(ldap_config, "groupOfNames", "schema", "group_base_dn")),
    )
    AUTH_LDAP_MIRROR_GROUPS = False

    # permissions based on groups
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {}

    ldap_group_login = dict_get(ldap_config, None, "groups", "login")
    if ldap_group_login:
        AUTH_LDAP_USER_FLAGS_BY_GROUP["is_active"] = ldap_group_login

    ldap_group_admin = dict_get(ldap_config, None, "groups", "admin")
    if ldap_group_admin:
        AUTH_LDAP_USER_FLAGS_BY_GROUP["is_staff"] = ldap_group_admin
        AUTH_LDAP_USER_FLAGS_BY_GROUP["is_superuser"] = ldap_group_admin

# OpenID Connect
oidc_config = dict_get(config, None, "authentication", "oidc")
OIDC_CUSTOM_PROVIDER_NAME = None  # used to check if enabled or not
OIDC_CUSTOM_LOGOUT_ENDPOINT = None
OIDC_CUSTOM_LOGOUT_REDIRECT_PARAMTER = None
if oidc_config:
    # name for identity provider displayed on login page (custom paremeter, not from lib)
    OIDC_CUSTOM_PROVIDER_NAME = dict_get(oidc_config, "OpenID Connect", "provider_name")

    # provider
    OIDC_RP_SIGN_ALGO = "RS256"
    OIDC_OP_JWKS_ENDPOINT = dict_get(oidc_config, None, "provider", "jwks_uri")

    OIDC_RP_CLIENT_ID = dict_get(oidc_config, None, "provider", "client_id")
    OIDC_RP_CLIENT_SECRET = dict_get(oidc_config, None, "provider", "client_secret")

    OIDC_OP_AUTHORIZATION_ENDPOINT = dict_get(oidc_config, None, "provider", "authorization_endpoint")
    OIDC_OP_TOKEN_ENDPOINT = dict_get(oidc_config, None, "provider", "token_endpoint")
    OIDC_OP_USER_ENDPOINT = dict_get(oidc_config, None, "provider", "user_endpoint")

    OIDC_RP_SCOPES = dict_get(oidc_config, "openid email profile", "provider", "scopes")

    oidc_renew_check_interval = dict_get(oidc_config, 0, "provider", "renew_check_interval")
    if oidc_renew_check_interval > 0:
        OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = oidc_renew_check_interval * 60

    # username is mail address
    OIDC_USERNAME_ALGO = "helfertool.oidc.generate_username"

    # login and logout
    LOGIN_REDIRECT_URL_FAILURE = "/oidc/failed"
    ALLOW_LOGOUT_GET_METHOD = True

    oidc_logout = dict_get(oidc_config, None, "provider", "logout")
    if oidc_logout:
        OIDC_CUSTOM_LOGOUT_ENDPOINT = dict_get(oidc_logout, None, "endpoint")
        OIDC_CUSTOM_LOGOUT_REDIRECT_PARAMTER = dict_get(oidc_logout, None, "redirect_parameter")

        OIDC_OP_LOGOUT_URL_METHOD = "helfertool.oidc.custom_oidc_logout"

    # claims for is_active and is_admin
    OIDC_CUSTOM_CLAIM_LOGIN = dict_get(oidc_config, None, "claims", "login")
    OIDC_CUSTOM_CLAIM_ADMIN = dict_get(oidc_config, None, "claims", "admin")

# django auth backends
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
]

if ldap_config:
    AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

if oidc_config:
    AUTHENTICATION_BACKENDS.append("helfertool.oidc.CustomOIDCAuthenticationBackend")

AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.ModelBackend")

# password policy
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": dict_get(config, 12, "security", "password_length"),
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# axes: user lockout based on username, not IP or user agent
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_LOCK_OUT_AT_FAILURE = True

AXES_FAILURE_LIMIT = dict_get(config, 5, "security", "lockout", "limit")
AXES_COOLOFF_TIME = lambda request: timedelta(minutes=dict_get(config, 10, "security", "lockout", "time"))

AXES_LOCKOUT_TEMPLATE = "helfertool/login_banned.html"
AXES_DISABLE_ACCESS_LOG = True
if OIDC_CUSTOM_PROVIDER_NAME is not None:
    AXES_WHITELIST_CALLABLE = "helfertool.oidc.axes_whitelist"

# security
DEBUG = dict_get(config, False, "security", "debug")
SECRET_KEY = dict_get(config, "CHANGEME", "security", "secret")
ALLOWED_HOSTS = dict_get(config, [], "security", "allowed_hosts") or []  # empty list in config is None, but we need []

CAPTCHAS_NEWSLETTER = dict_get(config, False, "security", "captchas", "newsletter")
CAPTCHAS_REGISTRATION = dict_get(config, False, "security", "captchas", "registration")

# use X-Forwarded-Proto header to determine if https is used (overwritten in settings_container.py)
if dict_get(config, False, "security", "behind_proxy"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# password hashers: use scrypt instead of PBKDF2
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# cookies
LANGUAGE_COOKIE_NAME = "lang"
LANGUAGE_COOKIE_HTTPONLY = True
LANGUAGE_COOKIE_SAMESITE = "Lax"
LANGUAGE_COOKIE_AGE = 31449600

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
# OIDC with foreign TLDs is blocked by SAMESITE=Strict, so make this configurable
if oidc_config and dict_get(oidc_config, False, "provider", "thirdparty_domain"):
    SESSION_COOKIE_SAMESITE = "Lax"
else:
    SESSION_COOKIE_SAMESITE = "Strict"

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    LANGUAGE_COOKIE_SECURE = True

# logging
ADMINS = [(mail, mail) for mail in dict_get(config, [], "logging", "mails")]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        # formatters for console and syslog. database logging does not use a formatter
        "helfertool_console": {
            "()": "toollog.formatters.TextFormatter",
            "format": "[%(asctime)s] %(levelname)s %(message)s (%(extras)s)",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "helfertool_syslog": {
            "()": "toollog.formatters.TextFormatter",
            "format": "helfertool %(levelname)s %(message)s (%(extras)s)",
        },
    },
    "handlers": {
        # console output in debug mode (-> development)
        "helfertool_console": {
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "helfertool_console",
            "level": "INFO",
        },
        # store in database (only event-related entries)
        "helfertool_database": {
            "class": "toollog.handlers.DatabaseHandler",
            "level": "INFO",
        }
        # syslog handlers are added dynamically below
    },
    "loggers": {
        "helfertool": {
            "handlers": ["helfertool_console"],
            "level": "INFO",
        },
    },
}

# enable database logging
DATABASE_LOGGING = dict_get(config, True, "logging", "database")
if DATABASE_LOGGING:
    LOGGING["loggers"]["helfertool"]["handlers"].append("helfertool_database")

# enable syslog if configured
# additional syslog handler is added in settings_container.py
syslog_config = dict_get(config, None, "logging", "syslog")
if syslog_config:
    protocol = dict_get(syslog_config, "udp", "protocol")
    if protocol not in ["tcp", "udp"]:
        print('Invalid syslog port: "tcp" or "udp" expected')
        sys.exit(1)

    LOGGING["handlers"]["helfertool_syslog"] = {
        "class": "logging.handlers.SysLogHandler",
        "formatter": "helfertool_syslog",
        "level": "INFO",
        "facility": dict_get(syslog_config, "local7", "facility"),
        "address": (dict_get(syslog_config, "localhost", "server"), dict_get(syslog_config, 514, "port")),
        "socktype": socket.SOCK_DGRAM if protocol == "udp" else socket.SOCK_STREAM,
    }

    LOGGING["loggers"]["helfertool"]["handlers"].append("helfertool_syslog")

# Helfertool features
FEATURES_NEWSLETTER = bool(dict_get(config, True, "features", "newsletter"))
FEATURES_BADGES = bool(dict_get(config, True, "features", "badges"))
FEATURES_GIFTS = bool(dict_get(config, True, "features", "gifts"))
FEATURES_PREREQUISITES = bool(dict_get(config, True, "features", "prerequisites"))
FEATURES_INVENTORY = bool(dict_get(config, True, "features", "inventory"))
FEATURES_CORONA = bool(dict_get(config, True, "features", "corona"))

# Display Options
# Maximum years of events to be displayed by default on the main page
EVENTS_LAST_YEARS = int(dict_get(config, 2, "customization", "display", "events_last_years"))
if EVENTS_LAST_YEARS < 0:
    print("events_show_years must be positive or 0")
    sys.exit(1)

# announcement on every page
ANNOUNCEMENT_TEXT = dict_get(config, None, "announcement")

# title for all pages
PAGE_TITLE = dict_get(config, "Helfertool", "customization", "title")

# external URLs
PRIVACY_URL = dict_get(config, "https://app.helfertool.org/datenschutz/", "customization", "urls", "privacy")
IMPRINT_URL = dict_get(config, "https://app.helfertool.org/impressum/", "customization", "urls", "imprint")
DOCS_URL = dict_get(config, "https://docs.helfertool.org", "customization", "urls", "docs")
WEBSITE_URL = "https://www.helfertool.org"

# mail address for "About this software" page and support requests
CONTACT_MAIL = dict_get(config, "helfertool@localhost", "customization", "contact_address")

# similarity search for postgresql
SEARCH_SIMILARITY = dict_get(config, 0.3, "customization", "search", "similarity")
SEARCH_SIMILARITY_DISABLED = dict_get(config, False, "customization", "search", "disable_similarity")

if SEARCH_SIMILARITY_DISABLED is False:
    # it only works on postgresql when pg_trgm is there, so check this. otherwise, disable
    if "postgresql" in DATABASES["default"]["ENGINE"]:
        if not pg_trgm_installed():
            SEARCH_SIMILARITY_DISABLED = True
    else:
        SEARCH_SIMILARITY_DISABLED = True

# badges
BADGE_PDFLATEX = dict_get(config, "/usr/bin/pdflatex", "badges", "pdflatex")
BADGE_PHOTO_MAX_SIZE = dict_get(config, 1000, "badges", "photo_max_size")
BADGE_SPECIAL_MAX = dict_get(config, 50, "badges", "special_badges_max")

BADGE_PDF_TIMEOUT = 60 * dict_get(config, 30, "badges", "pdf_timeout")
BADGE_RM_DELAY = 60 * dict_get(config, 2, "badges", "rm_delay")

BADGE_DEFAULT_TEMPLATE = build_path(
    dict_get(config, "src/badges/latextemplate/badge.tex", "badges", "template"), BASE_DIR
)

# copy generated latex code for badges to this file, disable with None
if DEBUG:
    BADGE_TEMPLATE_DEBUG_FILE = build_path("badge_debugging.tex", BASE_DIR)
else:
    BADGE_TEMPLATE_DEBUG_FILE = None

BADGE_LANGUAGE_CODE = dict_get(config, "de", "language", "badges")

# newsletter
NEWS_SUBSCRIBE_DEADLINE = dict_get(config, 3, "subscribe_deadline", "newsletter")

# internal group names
GROUP_ADDUSER = "registration_adduser"
GROUP_ADDEVENT = "registration_addevent"
GROUP_SENDNEWS = "registration_sendnews"

# Bootstrap config
BOOTSTRAP5 = {
    "required_css_class": "required-form",
}

# HTML sanitization for text fields
BLEACH_ALLOWED_TAGS = ["p", "b", "i", "u", "em", "strong", "a", "br", "ul", "ol", "li"]
BLEACH_ALLOWED_ATTRIBUTES = [
    "href",
]
BLEACH_ALLOWED_STYLES = []
BLEACH_STRIP_TAGS = True

# editor for text fields
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline"],
            [
                "NumberedList",
                "BulletedList",
                "-",
            ],
            ["Link", "Unlink"],
            ["Source"],
        ],
        # we want to have a responsive ckeditor:
        # 1. set width for editor itself here
        # 2. set width also vor div.django-ckeditor-widget via custom CSS
        "width": "100%",
    }
}

# django-select2 config
SELECT2_CACHE_BACKEND = "select2"

# django-icons config
DJANGO_ICONS = {
    "DEFAULTS": {
        "renderer": "fontawesome4",
    },
    "RENDERERS": {
        "fontawesome4": "FontAwesome4Renderer",
    },
}

# django-simple-captcha
CAPTCHA_FONT_SIZE = 30
CAPTCHA_IMAGE_SIZE = (120, 50)
CAPTCHA_LETTER_ROTATION = (-30, 30)
CAPTCHA_FOREGROUND_COLOR = "#1ea082"

# application definition
INSTALLED_APPS = (
    "helfertool",  # we override some default translations here, so put it first
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mozilla_django_oidc",
    "axes",
    "django_bootstrap5",
    "django_icons",
    "django_select2",
    "django_countries",
    "captcha",
    "ckeditor",
    "compressor",
    "django_celery_results",
    "registration.apps.RegistrationConfig",
    "statistic.apps.StatisticConfig",
    "badges.apps.BadgesConfig",
    "news.apps.NewsConfig",
    "gifts.apps.GiftsConfig",
    "inventory.apps.InventoryConfig",
    "mail.apps.MailConfig",
    "help.apps.HelpConfig",
    "account.apps.AccountConfig",
    "toolsettings.apps.ToolsettingsConfig",
    "prerequisites.apps.PrerequisitesConfig",
    "toollog.apps.ToollogConfig",
    "corona.apps.CoronaConfig",
)

# middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if oidc_config and oidc_renew_check_interval > 0:
    MIDDLEWARE.append("mozilla_django_oidc.middleware.SessionRefresh")

MIDDLEWARE.append("axes.middleware.AxesMiddleware")  # axes should be the last one

# templates and css/js compression
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "helfertool" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

COMPRESS_ENABLED = True  # compress also in debug mode
COMPRESS_OFFLINE = not DEBUG  # offline compression for prod deployments (overwritten in settings_container.py)
COMPRESS_OUTPUT_DIR = "compressed"
COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.CSSCompressorFilter",
    ],
    "js": [
        "compressor.filters.jsmin.JSMinFilter",
    ],
}

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)

# urls and wsgi things
ROOT_URLCONF = "helfertool.urls"

WSGI_APPLICATION = "helfertool.wsgi.application"
