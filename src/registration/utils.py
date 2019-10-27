import string


def escape_filename(filename):
    """Escape a filename so it includes only valid characters."""
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(char for char in filename if char in valid)
