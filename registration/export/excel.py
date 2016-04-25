from django.template import defaultfilters as filters
from django.utils.translation import ugettext as _
import re
import xlsxwriter

from ..utils import u


class Iterator():
    """ Returns ascending natural numbers beginning from 0. """
    def __init__(self):
        self.__v = -1

    def next(self):
        """ Returns the next number beginning from 0. """
        self.__v += 1
        return self.__v

    def get(self):
        """ Returns the current number.

        get() should only be used after next() to get the same number again.
        """
        return self.__v

    def reset(self):
        """ Resets the counter.

        The first call to next() after this returns 0. """
        self.__v = -1


def cleanName(name):
    """ Cleans the name to be a valid sheet name in excel.

    The characters [ ] : * ? / \ are removed.
    """
    return re.sub(r'[\[\]:*?\\\/]', '', name)


def xlsx(buffer, event, jobs):
    """ Exports the helpers for given jobs of an event as excel spreadsheet.

    Parameter:
        buffer: a writeable bytes buffer (e.g. io.BytesIO or a file)
        event:  the exported event
        jobs:   a list of all exported jobs
    """
    # create xlsx
    workbook = xlsxwriter.Workbook(buffer)

    # export jobs
    for job in jobs:
        worksheet = workbook.add_worksheet(cleanName(job.name))
        bold = workbook.add_format({'bold': True})
        multiple_shifts = workbook.add_format({'bg_color': '#FF6600'})

        row = Iterator()
        column = Iterator()

        # header
        worksheet.write(0, column.next(), _("First name"), bold)
        worksheet.write(0, column.next(), _("Surname"), bold)
        worksheet.write(0, column.next(), _("E-Mail"), bold)
        worksheet.set_column(0, column.get(), 30)

        worksheet.write(0, column.next(), _("Mobile phone"), bold)
        worksheet.set_column(column.get(), column.get(), 20)

        if event.ask_shirt:
            worksheet.write(0, column.next(), _("T-shirt"), bold)
            worksheet.set_column(column.get(), column.get(), 10)

        if event.ask_vegetarian:
            worksheet.write(0, column.next(), _("Vegetarian"), bold)
            worksheet.set_column(column.get(), column.get(), 13)

        if job.infection_instruction:
            worksheet.write(0, column.next(), _("Food handling"), bold)
            worksheet.set_column(column.get(), column.get(), 20)

        worksheet.write(0, column.next(), _("Comment"), bold)
        worksheet.set_column(column.get(), column.get(), 50)

        # last column, needed for merge later
        last_column = column.get()

        # freeze header
        worksheet.freeze_panes(1, 0)

        # skip first row
        row.next()

        # coordinators
        if job.coordinators.count() > 0:
            worksheet.merge_range(row.next(), 0, row.get(), last_column,
                                  _("Coordinators"), bold)
            add_helpers(worksheet, row, column, event, job,
                        job.coordinators.all(), multiple_shifts)

        # show all shifts
        for shift in job.shift_set.order_by('begin'):
            worksheet.merge_range(row.next(), 0, row.get(),
                                  last_column, shift.time(), bold)
            add_helpers(worksheet, row, column, event, job,
                        shift.helper_set.all(), multiple_shifts)

    # close xlsx
    workbook.close()


def add_helpers(worksheet, row, column, event, job, helpers,
                multiple_shifts_format):
    for helper in helpers:
        row.next()
        column.reset()

        num_shifts = helper.shifts.count()
        num_jobs = len(helper.coordinated_jobs)
        format = None
        if num_shifts + num_jobs > 1:
            format = multiple_shifts_format

        worksheet.write(row.get(), column.next(), helper.firstname, format)
        worksheet.write(row.get(), column.next(), helper.surname, format)
        worksheet.write(row.get(), column.next(), helper.email, format)
        worksheet.write(row.get(), column.next(), helper.phone, format)
        if event.ask_shirt:
            worksheet.write(row.get(), column.next(),
                            u(helper.get_shirt_display()), format)
        if event.ask_vegetarian:
            worksheet.write(row.get(), column.next(),
                            filters.yesno(helper.vegetarian), format)
        if job.infection_instruction:
            worksheet.write(row.get(), column.next(),
                            u(helper.get_infection_instruction_short()), format)
        worksheet.write(row.get(), column.next(), helper.comment, format)
