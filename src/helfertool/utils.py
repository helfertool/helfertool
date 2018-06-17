import os


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
