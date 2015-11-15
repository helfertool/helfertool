import string
import sys

import magic

def escape_filename(filename):
    """Escape a filename so it includes only valid characters."""
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(char for char in filename if char in valid)


# convert to unicode
if sys.version_info < (3,):
    def u(x):
        return unicode(x)
else:
    def u(x):
        return str(x)


# check if file is an image using libmagic
def is_image(file):
    filemime = magic.from_buffer(file.read(), mime=True)
    file.seek(0)

    return filemime.startswith(b'image/')
