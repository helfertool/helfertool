import os

from django.db import connection


def dict_get(data, default, *keys):
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default


def build_path(path, base_dir):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(base_dir, '..', path)


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
    with connection.cursor() as cursor:
        cursor.execute("select installed_version from pg_available_extensions where name='pg_trgm';")
        version = cursor.fetchone()[0]

        return version is not None
