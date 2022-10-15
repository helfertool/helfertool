from django.utils.translation import gettext as _

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# styles
par_style = getSampleStyleSheet()["Normal"]
h1_style = getSampleStyleSheet()["Heading1"]
h2_style = getSampleStyleSheet()["Heading2"]
table_style = TableStyle(
    [
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
)

margin = 1.5 * cm


def h1(text):
    return Paragraph(text, h1_style)


def h2(text):
    return Paragraph(text, h2_style)


def par(text):
    return Paragraph(text, par_style)


def add_table(elements, data, widths):
    t = Table(data, widths, hAlign="LEFT")
    t.setStyle(table_style)
    elements.append(t)


def table_of_helpers(elements, helpers, event):
    # table
    header = [
        par(_("Name")),
    ]
    spaces = [
        6,
    ]
    if event.ask_shirt:
        header.append(par(_("T-shirt")))
        spaces.append(2.5)
    header.append(par(_("Comment")))
    spaces.append(17 - sum(spaces))  # 17cm are the total possible width, adjust the comment column to fill that

    data = [
        header,
    ]

    for helper in helpers:
        tmp = [
            par("%s %s" % (helper.firstname, helper.surname)),
        ]
        if event.ask_shirt:
            tmp.append(par(helper.get_shirt_display()))
        tmp.append(par(helper.comment))
        data.append(tmp)

    spaces = [s * cm for s in spaces]
    add_table(elements, data, spaces)


def pdf(buffer, event, jobs, date):
    doc = SimpleDocTemplate(buffer, topMargin=margin, rightMargin=margin, bottomMargin=margin, leftMargin=margin)
    doc.pagesize = A4

    # elements
    elements = []

    # iterate over jobs
    for job in jobs:
        # heading
        heading = h1("%s" % job.name)
        elements.append(heading)

        # coordinators
        if not date and job.coordinators.exists():
            heading = h2(_("Coordinators"))
            elements.append(heading)

            table_of_helpers(elements, job.coordinators.all(), event)

        # iterate over shifts
        for shift in job.shift_set.all():
            if date and shift.date() != date:
                continue

            heading = h2(shift.time_with_day())
            elements.append(heading)

            if shift.helper_set.count() > 0:
                table_of_helpers(elements, shift.helper_set.all(), event)
            else:
                p = par(_("Nobody is registered for this shift."))
                elements.append(p)

        # page break
        elements.append(PageBreak())

    # build pdf
    doc.build(elements)
