"""
Django settings for Helfertool.

These are the default settings, do not change this file.
Copy settings_local.dist.py to settings_local.py and make changes there!
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys

from django.utils.translation import ugettext_lazy as _

from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

######################
#                    #
# Import local files #
#                    #
######################

try:
    from .settings_local import *
except ImportError:
    print("Local configuration missing!")
    print("")
    print("Please copy helfertool/settings_local.dist.py to "
          "helfertool/settings_local.py and adapt to your needs.")
    sys.exit(1)

######################################################################
#                                                                    #
# Django and internal stuff (override only if you know what you do!) #
#                                                                    #
######################################################################

# internal group names
GROUP_ADDUSER = "registration_adduser"
GROUP_ADDEVENT = "registration_addevent"
GROUP_SENDNEWS = "registration_sendnews"

# axes settings (relevant settings are in settings_local.py)
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USE_USER_AGENT = False
AXES_LOCKOUT_TEMPLATE = 'registration/login_banned.html'
AXES_BEHIND_REVERSE_PROXY = True

# file permissions for newly uploaded files
FILE_UPLOAD_PERMISSIONS = 0o640

# auth
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Bootstrap config
BOOTSTRAP3 = {
    'required_css_class': 'required',
}

# HTML sanitization for text fields
BLEACH_ALLOWED_TAGS = ['p', 'b', 'i', 'u', 'em', 'strong', 'a', 'br', 'ul',
                       'ol', 'li']
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'style']
BLEACH_ALLOWED_STYLES = ['font-weight', 'text-decoration']
BLEACH_STRIP_TAGS = True

# editor for text fields
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', ],
            ['Link', 'Unlink'],
            ['Source']
        ],
    }
}

# Application definition

INSTALLED_APPS = (
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',
    'djangobower',
    'bootstrap3',
    'ckeditor',
    'helfertool',
    'registration',
    'statistic',
    'badges',
    'news',
    'gifts',
    'inventory',
    'mail',
    'help',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

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

# Internationalization

# this is the default language
# it is also important when sending news mails (the text in this language will
# be first, the other languages follow)
LANGUAGE_CODE = 'de'

LANGUAGES = (
    ('de', _('German')),
    ('en', _('English')),
)

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Bower
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components')

BOWER_INSTALLED_APPS = (
    'jquery',
    'bootstrap#<4.0.0',
    'bootstrap3-datetimepicker',
    'bootstrap-duallistbox',
    'select2',
    'font-awesome',
    'chart.js',
    'datatables.net',
    'datatables.net-bs',
)

# file directories
STATIC_URL = '/static/'
MEDIA_URL = '/media/'  # must end with '/' !
