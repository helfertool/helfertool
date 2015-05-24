import string

def escape_filename(filename):
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(char for char in filename if char in valid)
