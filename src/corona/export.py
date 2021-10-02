from django.utils.translation import ugettext as _

import xlsxwriter
from io import BytesIO

from registration.export.excel import Iterator, escape

from .models import ContactTracingData


def excel_export(event):
    # create excel file in memory
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet(_("Corona contact tracing"))
    bold = workbook.add_format({'bold': True})

    row = Iterator()
    column = Iterator()
    row.next()  # we need to start at 1

    # header
    worksheet.write(row.get(), column.next(), _("First name"), bold)
    worksheet.write(row.get(), column.next(), _("Surname"), bold)
    worksheet.write(row.get(), column.next(), _("E-Mail"), bold)
    worksheet.write(row.get(), column.next(), _("Mobile phone"), bold)
    worksheet.write(row.get(), column.next(), _("Street and house number"), bold)
    worksheet.write(row.get(), column.next(), _("ZIP"), bold)
    worksheet.write(row.get(), column.next(), _("City"), bold)
    worksheet.write(row.get(), column.next(), _("Country"), bold)
    worksheet.write(row.get(), column.next(), _("Shifts and jobs"), bold)
    worksheet.freeze_panes(1, 0)
    row.next()

    for helper in event.helper_set.all():
        column.reset()

        worksheet.write(row.get(), column.next(), escape(helper.firstname))
        worksheet.write(row.get(), column.next(), escape(helper.surname))
        worksheet.write(row.get(), column.next(), escape(helper.email))
        worksheet.write(row.get(), column.next(), escape(helper.phone))

        try:
            data = helper.contacttracingdata
            worksheet.write(row.get(), column.next(), escape(data.street))
            worksheet.write(row.get(), column.next(), escape(data.zip))
            worksheet.write(row.get(), column.next(), escape(data.city))
            worksheet.write(row.get(), column.next(), escape(data.country.name))
        except ContactTracingData.DoesNotExist:
            column.add(4)

        shifts_and_jobs = []
        for job in helper.coordinated_jobs:
            shifts_and_jobs.append("{}: {}".format(_("Coordinator"), job.name))
        for shift in helper.shifts.all():
            shifts_and_jobs.append(str(shift))
        worksheet.write(row.get(), column.next(), escape("\n".join(shifts_and_jobs)))

        row.next()

    # return data
    workbook.close()
    data = buffer.getvalue()
    buffer.close()
    return data
