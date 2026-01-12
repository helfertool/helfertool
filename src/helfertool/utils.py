from django.core.cache import caches
from django.db import connection
from django.http import FileResponse, Http404
from django.shortcuts import render

from contextlib import contextmanager
from pathlib import Path

import time
import mimetypes


def dict_get(data, default, *keys):
    """
    Lookup in nested dict.

    Example:
        data = {
            "a" = 1,
            "b" = {
                "c": 2,
                "d": 3,
            }
        }

        dict_get(data, 0, "a")  # returns 1
        dict_get(data, 0, "b", "c")  # returns 2
        dict_get(data, 0, "c")  # returns 0 (the default value)

    Used on settings.py
    """
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default


def build_path(path, base_dir):
    """
    Build the path for a settings option.

    If absolute, return it. Otherwise, build it relative to the Git folder (on the level of `src`)
    """
    tmp_path = Path(path)
    if tmp_path.is_absolute():
        return tmp_path
    else:
        return base_dir.parent / tmp_path


def get_version(path):
    """
    Read the version from specified file or return `unknown`.
    """
    try:
        with open(path) as f:
            version = f.readlines()
            return version[0].strip() or "unknown"
    except (IOError, IndexError):
        return "unknown"


def pg_trgm_installed():
    """
    Check, if pg_trgm extension is installed in PostgreSQL server.
    """
    with connection.cursor() as cursor:
        cursor.execute("select installed_version from pg_available_extensions where name='pg_trgm';")
        version = cursor.fetchone()[0]

        return version is not None


@contextmanager
def cache_lock(lock_id, oid, expire=60 * 10):
    """
    A lock based on the Django caching functionality. Used in some Celery tasks to prevent
    the parallel execution of the same task (e.g. receiving mails).

    Source: https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html

    We use the database cache backend here, this is not as good as using memcached,
    but should be good enough for the use case. By default, the lock expires after 10 minutes.
    """
    timeout_at = time.monotonic() + expire - 3
    # cache.add fails if the key already exists
    status = caches["locks"].add(lock_id, oid, expire)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            caches["locks"].delete(lock_id)


def serve_file(file):
    """Reads a file from disk and returns FileReponse with the correct content type and encoding.

    Warning: The Content-Disposition header is not set, as it is currently used with images."""
    if not file:
        raise Http404

    content_type, encoding = mimetypes.guess_type(str(file))
    content_type = content_type or "application/octet-stream"

    response = FileResponse(file.open("rb"), content_type=content_type)
    if encoding:
        response.headers["Content-Encoding"] = encoding

    return response


def nopermission(request):
    """
    Render the "no permission" page".
    """
    return render(request, "helfertool/nopermission.html")


PROSE_EDITOR_DEFAULT_EXTENSIONS = {
    "Bold": True,
    "Italic": True,
    "Underline": True,
    "Strike": True,
    "BulletList": True,
    "OrderedList": True,
    "ListItem": True,
    "Link": {
        "protocols": ["http", "https", "mailto"],
    },
    "History": True,
    "HTML": True,
}
