import string
import sys


def escape_filename(filename):
    """Escape a filename so it includes only valid characters."""
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(char for char in filename if char in valid)


# convert to unicode
if sys.version_info < (3,):
    def u(x):
        # pylint: disable=E0602
        return unicode(x)
else:
    def u(x):
        return str(x)
