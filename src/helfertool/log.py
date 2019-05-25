import logging

# The logging part was inspired by the following blog entries and projects:
#
# https://lincolnloop.com/blog/django-logging-right-way/
# https://lincolnloop.com/blog/logging-systemds-journal-python/
# https://github.com/madzak/python-json-logger
# https://www.caktusgroup.com/blog/2013/09/18/central-logging-django-graylog2-and-graypy/


SKIP_ATTRS = (
    # all default attributes
    'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
    'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name',
    'pathname', 'process', 'processName', 'relativeCreated', 'stack_info',
    'thread', 'threadName',

    # custom things
    'event', 'job', 'shift', 'helper',
)


def add_entry(data, key, value):
    if key not in data:
        data[key] = value
    return data


def get_extra_attrs(record):
    """
    Extracts all extra attributes from the log record and additionally:

    * replaces "event" by "event_url" and "event_pk"
    * replaces "job" by "job_name" and "job_pk"
    * replaces "shift" by "shift_name" and "shift_pk"
    * replaces "helper" by "helper_name" and "helper_pk"
    """
    result = {}

    for k, v in record.__dict__.items():
        if k not in SKIP_ATTRS:
            result[k] = v

    # event
    if hasattr(record, 'event'):
        result = add_entry(result, "event_url", record.event.url_name)
        result = add_entry(result, "event_pk", record.event.pk)

    # job
    if hasattr(record, 'job') and record.job:
        result = add_entry(result, "job_name", record.job.name)
        result = add_entry(result, "job_pk", record.job.pk)

    # shift
    if hasattr(record, 'shift') and record.shift:
        result = add_entry(result, "shift_name", str(record.shift))
        result = add_entry(result, "shift_pk", record.shift.pk)

    # helper
    if hasattr(record, 'helper') and record.helper:
        result = add_entry(result, "helper_name", record.helper.full_name)
        result = add_entry(result, "helper_pk", record.helper.pk)

    return result


class HelfertoolFormatter(logging.Formatter):
    """
    Customer formatter that outputs log lines like this:

    INFO user created (user="hertle" added_user="foo")
    """
    def format(self, record):
        if not hasattr(record, 'extras'):
            extras = get_extra_attrs(record)
            extras = ["{}=\"{}\"".format(k, v) for k, v in extras.items()]
            extras = ' '.join(extras)

            setattr(record, 'extras', extras)

        return super().format(record)
