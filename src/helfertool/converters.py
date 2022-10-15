from django.utils.dateparse import parse_date


class DateConverter:
    regex = "[0-9]{2,4}-[0-9]{1,2}-[0-9]{1,2}"

    def to_python(self, value):
        tmp = parse_date(value)
        # parse_date returns None if input is not well formated, but we need a ValueError here
        if not tmp:
            raise ValueError("invalid date")
        return tmp

    def to_url(self, value):
        return value.strftime("%Y-%m-%d")
