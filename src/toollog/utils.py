SKIP_ATTRS = (
    # all default attributes
    'asctime', 'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
    'levelname', 'levelno', 'lineno', 'message', 'module', 'msecs', 'msg', 'name',
    'pathname', 'process', 'processName', 'relativeCreated', 'stack_info',
    'thread', 'threadName',

    # custom things
    'event', 'job', 'shift', 'helper', "user",

    # the TextFormatter set the "extras" attribute
    "extras",
)


def get_extras(record):
    """
    Extracts all extra attributes from the log record without changes.
    It just removes the default attributes and also the user, event, job, shift and helper.
    """
    result = {}

    for k, v in record.__dict__.items():
        if k not in SKIP_ATTRS:
            result[k] = v

    return result


def get_extras_with_replacement(record):
    """
    Extracts all extra attributes from the log record and additionally:

    * replaces "event" by "event_url" and "event_pk"
    * replaces "job" by "job_name" and "job_pk"
    * replaces "shift" by "shift_name" and "shift_pk"
    * replaces "helper" by "helper_name" and "helper_pk"
    * replaces "user" (the object) by "user" (the username as string)
    """
    result = get_extras(record)

    # event
    if hasattr(record, 'event'):
        result = _add_entry(result, "event_url", record.event.url_name)
        result = _add_entry(result, "event_pk", record.event.pk)

    # job
    if hasattr(record, 'job') and record.job:
        result = _add_entry(result, "job_name", record.job.name)
        result = _add_entry(result, "job_pk", record.job.pk)

    # shift
    if hasattr(record, 'shift') and record.shift:
        result = _add_entry(result, "shift_name", str(record.shift))
        result = _add_entry(result, "shift_pk", record.shift.pk)

    # helper
    if hasattr(record, 'helper') and record.helper:
        result = _add_entry(result, "helper_name", record.helper.full_name)
        result = _add_entry(result, "helper_pk", record.helper.pk)

    # user
    if hasattr(record, 'user') and record.user:
        # sometimes, we need to resolve the username, sometimes we directly receive it
        if type(record.user) == str:
            result = _add_entry(result, "user", record.user)
        else:
            result = _add_entry(result, "user", record.user.username)

    return result


def _add_entry(data, key, value):
    """
    Adds an entry to a dict if it does not exist already.
    If the key exists already, the dict is not changed.
    """
    if key not in data:
        data[key] = value
    return data
