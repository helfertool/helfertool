from django.template import defaultfilters as filters
import xlsxwriter

def xlsx(buffer, jobs):
    # create xlsx
    workbook = xlsxwriter.Workbook(buffer)

    # export jobs
    for job in jobs:
        worksheet = workbook.add_worksheet(job.name)
        bold = workbook.add_format({'bold': True})

        # header
        worksheet.write(0, 0, "Vorname", bold)
        worksheet.write(0, 1, "Nachname", bold)
        worksheet.write(0, 2, "E-Mail", bold)
        worksheet.write(0, 3, "Handy", bold)
        worksheet.write(0, 4, "T-Shirt", bold)
        worksheet.write(0, 5, "Vegetarier", bold)
        worksheet.write(0, 6, "Kommentar", bold)

        worksheet.freeze_panes(1, 0)
        worksheet.set_column(0, 3, 30)
        worksheet.set_column(4, 5, 10)
        worksheet.set_column(6, 6, 30)

        # the current row
        row=1

        # show all shifts
        for shift in job.shift_set.order_by('begin'):
            worksheet.merge_range(row, 0, row, 6, shift.time(), bold)
            row += 1
            for helper in shift.helper_set.all():
                worksheet.write(row, 0, helper.prename)
                worksheet.write(row, 1, helper.surname)
                worksheet.write(row, 2, helper.email)
                worksheet.write(row, 3, helper.phone)
                worksheet.write(row, 4, helper.get_shirt_display())
                worksheet.write(row, 5, filters.yesno(helper.vegetarian))
                worksheet.write(row, 6, helper.comment)
                row += 1

    # close xlsx
    workbook.close()
