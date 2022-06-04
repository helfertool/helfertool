from django.apps import AppConfig

# The logging part was inspired by the following blog entries and projects:
#
# https://lincolnloop.com/blog/django-logging-right-way/
# https://lincolnloop.com/blog/logging-systemds-journal-python/
# https://github.com/madzak/python-json-logger
# https://www.caktusgroup.com/blog/2013/09/18/central-logging-django-graylog2-and-graypy/


class ToollogConfig(AppConfig):
    name = "toollog"
