"""
Local configuration for Helfertool.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CHANGE-ME-AFTER-INSTALL'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = []

# recipients for error messages
ADMINS = (('Admin Name', 'admin@localhost'), )

# prepend character to local usernames (useful for LDAP/AD integration with
# local accounts parallely)
LOCAL_USER_CHAR = None

# directories for static and media files
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Message broker (RabbitMQ)
CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1/'
CELERY_RESULT_BACKEND = 'amqp://guest:guest@127.0.0.1/'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

# Mail settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

# sender of all mails (because of SPF, DKIM, DMARC)
FROM_MAIL = 'helfertool@localhost'

# mail shown on "About" page and for support requests
CONTACT_MAIL = 'helfertool@localhost'

# external URLs
PRIVACY_URL = 'https://app.helfertool.org/datenschutz/'
IMPRINT_URL = 'https://app.helfertool.org/impressum/'
WEBSITE_URL = 'https://www.helfertool.org'
DOCS_URL = 'https://docs.helfertool.org'

# axes: restrict login failures
AXES_LOGIN_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = timedelta(minutes=10)
AXES_REVERSE_PROXY_HEADER = 'REMOTE_ADDR'

# badges
BADGE_PDFLATEX = '/usr/bin/pdflatex'
BADGE_PHOTO_MAX_SIZE = 1000

BADGE_PDF_TIMEOUT = 30*60  # 30 minutes
BADGE_RM_DELAY = 2*60  # 2 minutes

BADGE_LANGUAGE_CODE = 'de'

BADGE_DEFAULT_TEMPLATE = os.path.join(BASE_DIR, 'badges', 'latextemplate',
                                      'badge.tex')

# copy generated latex code for badges to this file, disable with None
if DEBUG:
    BADGE_TEMPLATE_DEBUG_FILE = "/tmp/badge.tex"
else:
    BADGE_TEMPLATE_DEBUG_FILE = None

# Newsletter
# number of mails sent during one connection
MAIL_BATCH_SIZE = 200

# time between two connections in seconds
MAIL_BATCH_GAP = 5

# Logging
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'django.log'),
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#         },
#     },
#     'loggers': {
#         #'django.request': {
#         #    'handlers': ['file'],
#         #    'level': 'DEBUG',
#         #    'propagate': True,
#         #},
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#     },
# }
