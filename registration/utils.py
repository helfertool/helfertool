import string
import sys

def escape_filename(filename):
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(char for char in filename if char in valid)

if sys.version_info < (3,):
    def u(x):
        return unicode(x)
else:
    def u(x):
        return str(x)
