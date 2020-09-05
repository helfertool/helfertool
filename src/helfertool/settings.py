"""
Django settings for Helfertool.
"""

import os
import socket
import sys
import yaml

from django.utils.translation import ugettext_lazy as _

from datetime import timedelta

from .utils import dict_get, build_path, get_version, pg_trgm_installed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# import configuration file
config_file = os.environ.get('HELFERTOOL_CONFIG_FILE',
                             os.path.join(BASE_DIR, 'helfertool.yaml'))

try:
    with open(config_file, 'r') as f:
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

# check if docker deployment
is_docker = dict_get(config, False, 'docker')

# versioning
HELFERTOOL_VERSION = get_version(os.path.join(BASE_DIR, 'version.txt'))
HELFERTOOL_CONTAINER_VERSION = None
if is_docker:
    HELFERTOOL_CONTAINER_VERSION = get_version('/helfertool/container_version')

# directories for static and media files
if is_docker:
    STATIC_ROOT = "static"
    MEDIA_ROOT = "/data/media"
    TMP_ROOT = "/data/tmp"
else:
    STATIC_ROOT = build_path(dict_get(config, 'static', 'files', 'static'),
                             BASE_DIR)
    MEDIA_ROOT = build_path(dict_get(config, 'media', 'files', 'media'),
                            BASE_DIR)

    # directory for temporary files (badges, file uploads)
    TMP_ROOT = build_path(dict_get(config, '/tmp', 'files', 'tmp'),
                          BASE_DIR)

STATIC_URL = '/static/'
MEDIA_URL = '/media/'


# file permissions for newly uploaded files and directories
FILE_UPLOAD_PERMISSIONS = 0o640
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o750
FILE_UPLOAD_TEMP_DIR = TMP_ROOT

# internationalization
LANGUAGE_CODE = dict_get(config, 'de', 'language', 'default')

TIME_ZONE = dict_get(config, 'Europe/Berlin', 'language', 'timezone')

LANGUAGES = (
    ('de', _('German')),
    ('en', _('English')),
)

USE_I18N = True
USE_L10N = True
USE_TZ = True

# database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + dict_get(config, 'sqlite3',
                                                   'database', 'backend'),
        'NAME': dict_get(config, 'db.sqlite3', 'database', 'name'),
        'USER': dict_get(config, None, 'database', 'user'),
        'PASSWORD': dict_get(config, None, 'database', 'password'),
        'HOST': dict_get(config, None, 'database', 'host'),
        'PORT': dict_get(config, None, 'database', 'port'),
        'OPTIONS': dict_get(config, {}, 'database', 'options'),
    }
}

# build correct relative path for sqlite (if necessary)
if 'sqlite3' in DATABASES['default']['ENGINE']:
    DATABASES['default']['NAME'] = build_path(DATABASES['default']['NAME'],
                                              BASE_DIR)

# rabbitmq
CELERY_BROKER_URL = 'amqp://{}:{}@{}:{}/{}'.format(
    dict_get(config, 'guest', 'rabbitmq', 'user'),
    dict_get(config, 'guest', 'rabbitmq', 'password'),
    dict_get(config, 'localhost', 'rabbitmq', 'host'),
    dict_get(config, '5672', 'rabbitmq', 'port'),
    dict_get(config, '', 'rabbitmq', 'vhost'),
)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_BROKER_POOL_LIMIT = None

# caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'select2': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'select2_cache',
    },
    'locks': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'locks_cache',
    },
}

# mail
if dict_get(config, None, 'mail', 'host') is None:
    # new config format: sending and receiving mails separated

    # send
    EMAIL_HOST = dict_get(config, 'localhost', 'mail', 'send', 'host')
    EMAIL_PORT = dict_get(config, 25, 'mail', 'send', 'port')
    EMAIL_HOST_USER = dict_get(config, None, 'mail', 'send', 'user')
    EMAIL_HOST_PASSWORD = dict_get(config, None, 'mail', 'send', 'password')
    EMAIL_USE_SSL = dict_get(config, False, 'mail', 'send', 'tls')
    EMAIL_USE_TLS = dict_get(config, False, 'mail', 'send', 'starttls')

    if EMAIL_USE_SSL and EMAIL_USE_TLS:
        print("Mail settings for sending invalid: TLS and STARTTLS are mutually exclusive")
        sys.exit(1)

    # receive
    RECEIVE_EMAIL_HOST = dict_get(config, None, 'mail', 'receive', 'host')
    RECEIVE_EMAIL_PORT = dict_get(config, None, 'mail', 'receive', 'port')
    RECEIVE_EMAIL_HOST_USER = dict_get(config, None, 'mail', 'receive', 'user')
    RECEIVE_EMAIL_HOST_PASSWORD = dict_get(config, None, 'mail', 'receive', 'password')
    RECEIVE_EMAIL_USE_SSL = dict_get(config, False, 'mail', 'receive', 'tls')
    RECEIVE_EMAIL_USE_TLS = dict_get(config, False, 'mail', 'receive', 'starttls')

    RECEIVE_EMAIL_FOLDER = dict_get(config, 'INBOX', 'mail', 'receive', 'folder')
    RECEIVE_INTERVAL = dict_get(config, 300, 'mail', 'receive', 'interval')

    if RECEIVE_EMAIL_USE_SSL and RECEIVE_EMAIL_USE_TLS:
        print("Mail settings for receiving invalid: TLS and STARTTLS are mutually exclusive")
        sys.exit(1)
else:
    # old config format
    EMAIL_HOST = dict_get(config, 'localhost', 'mail', 'host')
    EMAIL_PORT = dict_get(config, 25, 'mail', 'port')
    EMAIL_HOST_USER = dict_get(config, None, 'mail', 'user')
    EMAIL_HOST_PASSWORD = dict_get(config, None, 'mail', 'password')
    EMAIL_USE_TLS = dict_get(config, False, 'mail', 'tls')

# sender of all mails (because of SPF, DKIM, DMARC)
# the display name defaults to the mail address
EMAIL_SENDER_ADDRESS = dict_get(config, 'helfertool@localhost', 'mail', 'sender_address')
EMAIL_SENDER_NAME = dict_get(config, EMAIL_SENDER_ADDRESS, 'mail', 'sender_name')

SERVER_EMAIL = EMAIL_SENDER_ADDRESS  # for error messages

# forward mails that were not handled automatically to this address
# the display name defaults to the mail address
FORWARD_UNHANDLED_ADDRESS = dict_get(config, None, 'mail', 'forward_unhandled_address')
FORWARD_UNHANDLED_NAME = dict_get(config, FORWARD_UNHANDLED_ADDRESS, 'mail', 'forward_unhandled_name')

# newsletter: number of mails sent during one connection and time between
MAIL_BATCH_SIZE = dict_get(config, 200, 'mail', 'batch_size')
MAIL_BATCH_GAP = dict_get(config, 5, 'mail', 'batch_gap')

# authentication
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/manage/account/check/'

LOCAL_USER_CHAR = dict_get(config, None, 'authentication', 'local_user_char')

# LDAP
ldap_config = dict_get(config, None, 'authentication', 'ldap')
if ldap_config:
    import django_auth_ldap.config
    import ldap

    # server address and authentication
    AUTH_LDAP_SERVER_URI = dict_get(ldap_config, 'ldaps://localhost', 'server',
                                    'host')
    AUTH_LDAP_BIND_DN = dict_get(ldap_config, None, 'server', 'bind_dn')
    AUTH_LDAP_BIND_PASSWORD = dict_get(ldap_config, None, 'server',
                                       'bind_password')

    # user schema
    AUTH_LDAP_USER_DN_TEMPLATE = dict_get(ldap_config, None, 'schema',
                                          'user_dn_template')
    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': dict_get(ldap_config, 'givenName', 'schema',
                               'first_name_attr'),
        'last_name': dict_get(ldap_config, 'sn', 'schema', 'last_name_attr'),
        'email': dict_get(ldap_config, 'mail', 'schema', 'email_attr'),
    }

    # group schema
    group_type_name = dict_get(ldap_config, 'GroupOfNamesType', 'schema',
                               'group_type')
    AUTH_LDAP_GROUP_TYPE = getattr(django_auth_ldap.config, group_type_name)()

    AUTH_LDAP_GROUP_SEARCH = django_auth_ldap.config.LDAPSearch(
        dict_get(ldap_config, None, 'schema', 'group_base_dn'),
        ldap.SCOPE_SUBTREE,  # pylint: disable=E1101
        "(objectClass={})".format(dict_get(ldap_config, 'groupOfNames',
                                           'schema', 'group_base_dn'))
    )
    AUTH_LDAP_MIRROR_GROUPS = False

    # permissions based on groups
    AUTH_LDAP_USER_FLAGS_BY_GROUP = {}

    ldap_group_login = dict_get(ldap_config, None, 'groups', 'login')
    if ldap_group_login:
        AUTH_LDAP_USER_FLAGS_BY_GROUP['is_active'] = ldap_group_login

    ldap_group_admin = dict_get(ldap_config, None, 'groups', 'admin')
    if ldap_group_admin:
        AUTH_LDAP_USER_FLAGS_BY_GROUP['is_staff'] = ldap_group_admin
        AUTH_LDAP_USER_FLAGS_BY_GROUP['is_superuser'] = ldap_group_admin

# OpenID Connect
oidc_config = dict_get(config, None, 'authentication', 'oidc')
OIDC_CUSTOM_PROVIDER_NAME = None  # used to check if enabled or not
if oidc_config:
    # name for identity provider displayed on login page (custom paremeter, not from lib)
    OIDC_CUSTOM_PROVIDER_NAME = dict_get(oidc_config, "OpenID Connect", 'provider_name')

    # provider
    OIDC_RP_SIGN_ALGO = 'RS256'
    OIDC_OP_JWKS_ENDPOINT = dict_get(oidc_config, None, 'provider', 'jwks_uri')

    OIDC_RP_CLIENT_ID = dict_get(oidc_config, None, 'provider', 'client_id')
    OIDC_RP_CLIENT_SECRET = dict_get(oidc_config, None, 'provider', 'client_secret')

    OIDC_OP_AUTHORIZATION_ENDPOINT = dict_get(oidc_config, None, 'provider', 'authorization_endpoint')
    OIDC_OP_TOKEN_ENDPOINT = dict_get(oidc_config, None, 'provider', 'token_endpoint')
    OIDC_OP_USER_ENDPOINT = dict_get(oidc_config, None, 'provider', 'user_endpoint')

    OIDC_RP_SCOPES = "openid email profile"  # also ask for profile -> given_name and family_name

    # username is mail address
    OIDC_USERNAME_ALGO = "helfertool.oidc.generate_username"

    LOGIN_REDIRECT_URL_FAILURE = "/oidc/failed"

    # claims for is_active and is_admin
    OIDC_CUSTOM_CLAIM_LOGIN = dict_get(oidc_config, None, 'claims', 'login')
    OIDC_CUSTOM_CLAIM_ADMIN = dict_get(oidc_config, None, 'claims', 'admin')

# django auth backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
]

if ldap_config:
    AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

if oidc_config:
    AUTHENTICATION_BACKENDS.append('helfertool.oidc.CustomOIDCAuthenticationBackend')

AUTHENTICATION_BACKENDS.append('django.contrib.auth.backends.ModelBackend')

# password policy
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': dict_get(config, 12, 'security', 'password_length'),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# axes: user lockout based on username, not IP or user agent
AXES_LOCK_OUT_AT_FAILURE = True
AXES_ONLY_USER_FAILURES = True
AXES_USE_USER_AGENT = False

AXES_FAILURE_LIMIT = dict_get(config, 3, 'security', 'lockout', 'limit')
AXES_COOLOFF_TIME = timedelta(minutes=dict_get(config, 10, 'security',
                                               'lockout', 'time'))

AXES_LOCKOUT_TEMPLATE = 'helfertool/login_banned.html'
AXES_DISABLE_ACCESS_LOG = True
if OIDC_CUSTOM_PROVIDER_NAME is not None:
    AXES_WHITELIST_CALLABLE = "helfertool.oidc.axes_whitelist"

# security
DEBUG = dict_get(config, False, 'security', 'debug')
SECRET_KEY = dict_get(config, 'CHANGEME', 'security', 'secret')
ALLOWED_HOSTS = dict_get(config, [], 'security', 'allowed_hosts')

# use X-Forwarded-* headers
if dict_get(config, False, 'security', 'behind_proxy') or is_docker:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# cookie security
if not DEBUG:
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Strict"

# logging
ADMINS = [(mail, mail) for mail in dict_get(config, [], 'logging', 'mails')]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'helfertool_console': {
            '()': 'toollog.formatters.TextFormatter',
            'format': '[%(asctime)s] %(levelname)s %(message)s (%(extras)s)',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
        'helfertool_syslog': {
            '()': 'toollog.formatters.TextFormatter',
            'format': '%(name)s %(levelname)s %(message)s (%(extras)s)',
        },
    },
    'handlers': {
        'helfertool_console': {
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'helfertool_console',
            'level': 'INFO',
        },
    },
    'loggers': {
        'helfertool': {
            'handlers': ['helfertool_console'],
            'level': 'INFO',
        },
    },
}

syslog_config = dict_get(config, None, 'logging', 'syslog')
if syslog_config:
    protocol = dict_get(syslog_config, 'udp', 'protocol')
    if protocol not in ['tcp', 'udp']:
        print('Invalid syslog port: "tcp" or "udp" expected')
        sys.exit(1)

    LOGGING['handlers']['helfertool_syslog'] = {
        'class': 'logging.handlers.SysLogHandler',
        'formatter': 'helfertool_syslog',
        'level': 'INFO',
        'facility': dict_get(syslog_config, 'local7', 'facility'),
        'address': (dict_get(syslog_config, 'localhost', 'server'),
                    dict_get(syslog_config, 514, 'port')),
        'socktype': socket.SOCK_DGRAM if protocol == 'udp' else socket.SOCK_STREAM,
    }

    LOGGING['loggers']['helfertool']['handlers'].append('helfertool_syslog')

if is_docker:
    LOGGING['handlers']['helfertool_syslog_docker'] = {
        'class': 'logging.handlers.SysLogHandler',
        'formatter': 'helfertool_syslog',
        'level': 'INFO',
        'facility': 'local7',
        'address': ('localhost', 5140),
    }

    LOGGING['loggers']['helfertool']['handlers'].append('helfertool_syslog_docker')

# Display Options
# Maximum years of events to be displayed by default on the main page
EVENTS_LAST_YEARS = int(dict_get(config, 2, 'customization', 'display', 'events_last_years'))
if EVENTS_LAST_YEARS < 0:
    print("events_show_years must be positive or 0")
    sys.exit(1)

# announcement on every page
ANNOUNCEMENT_TEXT = dict_get(config, None, 'announcement')

# external URLs
PRIVACY_URL = dict_get(config, 'https://app.helfertool.org/datenschutz/',
                       'customization', 'urls', 'privacy')
IMPRINT_URL = dict_get(config, 'https://app.helfertool.org/impressum/',
                       'customization', 'urls', 'imprint')
DOCS_URL = dict_get(config, 'https://docs.helfertool.org',
                    'customization', 'urls', 'docs')
WEBSITE_URL = 'https://www.helfertool.org'

# mail address for "About this software" page and support requests
CONTACT_MAIL = dict_get(config, 'helfertool@localhost', 'customization',
                        'contact_address')

# similarity search for postgresql
SEARCH_SIMILARITY = dict_get(config, 0.3, 'customization', 'search', 'similarity')
SEARCH_SIMILARITY_DISABLED = dict_get(config, False, 'customization', 'search', 'disable_similarity')

if SEARCH_SIMILARITY_DISABLED is False:
    # it only works on postgresql when pg_trgm is there, so check this. otherwise, disable
    if 'postgresql' in DATABASES['default']['ENGINE']:
        if not pg_trgm_installed():
            SEARCH_SIMILARITY_DISABLED = True
    else:
        SEARCH_SIMILARITY_DISABLED = True

# badges
BADGE_PDFLATEX = dict_get(config, '/usr/bin/pdflatex', 'badges', 'pdflatex')
BADGE_PHOTO_MAX_SIZE = dict_get(config, 1000, 'badges', 'photo_max_size')

BADGE_PDF_TIMEOUT = 60 * dict_get(config, 30, 'badges', 'pdf_timeout')
BADGE_RM_DELAY = 60 * dict_get(config, 2, 'badges', 'rm_delay')

BADGE_DEFAULT_TEMPLATE = build_path(
    dict_get(config, 'src/badges/latextemplate/badge.tex', 'badges',
             'template'),
    BASE_DIR)

# copy generated latex code for badges to this file, disable with None
if DEBUG:
    BADGE_TEMPLATE_DEBUG_FILE = build_path('badge_debugging.tex', BASE_DIR)
else:
    BADGE_TEMPLATE_DEBUG_FILE = None

BADGE_LANGUAGE_CODE = dict_get(config, 'de', 'language', 'badges')

# internal group names
GROUP_ADDUSER = "registration_adduser"
GROUP_ADDEVENT = "registration_addevent"
GROUP_SENDNEWS = "registration_sendnews"

# Bootstrap config
BOOTSTRAP4 = {
    'required_css_class': 'required',
}

# HTML sanitization for text fields
BLEACH_ALLOWED_TAGS = ['p', 'b', 'i', 'u', 'em', 'strong', 'a', 'br', 'ul',
                       'ol', 'li']
BLEACH_ALLOWED_ATTRIBUTES = ['href', ]
BLEACH_ALLOWED_STYLES = []
BLEACH_STRIP_TAGS = True

# editor for text fields
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', ],
            ['Link', 'Unlink'],
            ['Source']
        ],
    }
}

# django-select2 config
SELECT2_CACHE_BACKEND = 'select2'

# application definition
INSTALLED_APPS = (
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
    'mozilla_django_oidc',
    'axes',
    'bootstrap4',
    'django_icons',
    'django_select2',
    'ckeditor',
    'registration.apps.RegistrationConfig',
    'statistic.apps.StatisticConfig',
    'badges.apps.BadgesConfig',
    'news.apps.NewsConfig',
    'gifts.apps.GiftsConfig',
    'inventory.apps.InventoryConfig',
    'mail.apps.MailConfig',
    'help.apps.HelpConfig',
    'account.apps.AccountConfig',
    'toolsettings.apps.ToolsettingsConfig',
    'prerequisites.apps.PrerequisitesConfig',
    'toollog.apps.ToollogConfig',
    'helfertool',
)

# middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

if oidc_config:
    MIDDLEWARE.append('mozilla_django_oidc.middleware.SessionRefresh')

MIDDLEWARE.append('axes.middleware.AxesMiddleware')  # axes should be the last one

# urls and templates
ROOT_URLCONF = 'helfertool.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,  'helfertool', 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'helfertool.wsgi.application'
