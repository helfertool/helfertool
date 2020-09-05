import logging

from .utils import get_extra_attrs


class TextFormatter(logging.Formatter):
    """
    Customer formatter that outputs log lines like this:

    INFO user created (user="hertle" added_user="foo")
    """
    def format(self, record):
        if not hasattr(record, 'extras'):
            extras = get_extra_attrs(record)
            extras = ["{}=\"{}\"".format(k, v) for k, v in extras.items()]
            extras = ' '.join(extras)

            setattr(record, 'extras', extras)

        return super().format(record)
