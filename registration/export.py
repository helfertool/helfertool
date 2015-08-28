from django.template import defaultfilters as filters
from django.utils.translation import ugettext as _
import re
import xlsxwriter

from .utils import u

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

        column = Iterator()

        # header
        worksheet.write(0, column.next(), _("Prename"), bold)
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

        # the current row
        row=1

        # show all shifts
        for shift in job.shift_set.order_by('begin'):
            worksheet.merge_range(row, 0, row, last_column, shift.time(), bold)
            row += 1
            for helper in shift.helper_set.all():
                column.reset()
                worksheet.write(row, column.next(), helper.prename)
                worksheet.write(row, column.next(), helper.surname)
                worksheet.write(row, column.next(), helper.email)
                worksheet.write(row, column.next(), helper.phone)
                if event.ask_shirt:
                    worksheet.write(row, column.next(), u(helper.get_shirt_display()))
                if event.ask_vegetarian:
                    worksheet.write(row, column.next(), filters.yesno(helper.vegetarian))
                if job.infection_instruction:
                    worksheet.write(row, column.next(), u(helper.get_infection_instruction_short()))
                worksheet.write(row, column.next(), helper.comment)
                row += 1

    # close xlsx
    workbook.close()
