import logging

from .utils import get_extras_with_replacement


class TextFormatter(logging.Formatter):
    """
    Customer formatter that outputs log lines like this:

    INFO user created (user="hertle" added_user="foo")
    """
    def format(self, record):
        if not hasattr(record, 'extras'):
            extras = get_extras_with_replacement(record)
            extras = ["{}=\"{}\"".format(k, v) for k, v in extras.items()]
            extras = ' '.join(extras)

            setattr(record, 'extras', extras)

        return super().format(record)
