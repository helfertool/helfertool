import magic


# check if file is an image using libmagic
def is_image(file):
    filemime = magic.from_buffer(file.read(), mime=True)
    file.seek(0)

    return filemime.startswith('image/')
