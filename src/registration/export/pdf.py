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
        ("ROWMINHEIGHT", (0, 0), (-1, -1), 0.6 * cm),
    ]
)

names_per_line = 3
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


def table_of_helpers(elements, helpers, event, add_mobile_number=False, concat_comments=False):
    # table
    header = [
        par(_("Name")),
    ]
    spaces = [
        6,
    ]
    if add_mobile_number:
        header.append(par(_("Mobile phone")))
        spaces.append(3)
    if event.ask_shirt:
        header.append(par(_("T-shirt")))
        spaces.append(2.5)
    header.append(par(_("Comment")))
    spaces.append(17 - sum(spaces))  # 17cm are the total possible width, adjust the comment column to fill that

    data = [
        header,
    ]

    if concat_comments:
        helpers = concatenate_comments(helpers)

    for helper in helpers:
        tmp = [
            par("%s %s" % (helper.firstname, helper.surname)),
        ]
        if add_mobile_number:
            tmp.append(par(helper.phone))
        if event.ask_shirt:
            tmp.append(par(helper.get_shirt_display()))
        tmp.append(par(helper.comment))
        data.append(tmp)

    spaces = [s * cm for s in spaces]
    add_table(elements, data, spaces)


def table_of_helper_slots(
    elements, registered_helpers, number_of_shifts, all_helpers
):  # Potentiell mit den anderen tabel-funktionen zusammenführen
    data = []
    num_helpers = len(registered_helpers)
    for num in range(number_of_shifts):
        if num < num_helpers:
            helper = registered_helpers[num]
            data.append(par("%s %s" % (helper.firstname, helper.surname)))
            all_helpers.add(helper)
        else:
            data.append(par("&nbsp;"))

    data = [data[i : i + names_per_line] for i in range(0, len(data), names_per_line)]

    spaces = [(17 / names_per_line) * cm for n in range(names_per_line)]
    add_table(elements, data, spaces)


def pdf(buffer, event, jobs, date, handnote_optimized=False):
    doc = SimpleDocTemplate(buffer, topMargin=margin, rightMargin=margin, bottomMargin=margin, leftMargin=margin)
    doc.pagesize = A4

    # elements
    elements = []
    # collection of all helpers
    all_helpers = set()
    # iterate over jobs
    for job in jobs:
        # heading
        heading = h1("%s" % job.name)
        elements.append(heading)

        # coordinators
        if not date and job.coordinators.exists():
            heading = h2(_("Coordinators"))
            elements.append(heading)

            coordinators = job.coordinators.all()

            if handnote_optimized:
                table_of_helper_slots(elements, coordinators, len(coordinators), all_helpers)
            else:
                table_of_helpers(elements, coordinators, event)

        # iterate over shifts
        for shift in job.shift_set.all():
            if date and shift.date() != date:
                continue

            if handnote_optimized:
                heading = h2(shift.name)
                elements.append(heading)

                date_str = par(shift.time_with_day())
                elements.append(date_str)

                table_of_helper_slots(elements, shift.helper_set.all(), shift.number, all_helpers)
            else:
                heading = h2(shift.time_with_day())
                elements.append(heading)

                if shift.helper_set.count() > 0:
                    table_of_helpers(elements, shift.helper_set.all(), event)
                else:
                    p = par(_("Nobody is registered for this shift."))
                    elements.append(p)

        # page break
        elements.append(PageBreak())

    if handnote_optimized:
        # heading
        heading = h1(_("All helpers"))
        elements.append(heading)

        table_of_helpers(elements, all_helpers, event, add_mobile_number=True, concat_comments=True)

    # build pdf
    doc.build(elements)


def concatenate_comments(helpers):
    helper_dict = {}

    for helper in helpers:
        key = (
            helper.firstname,
            helper.surname,
            helper.phone,
            helper.get_shirt_display() if helper.event.ask_shirt else None,
        )

        if key in helper_dict.keys():
            helper_dict[key].comment = helper_dict[key].comment + " | " + helper.comment
        else:
            helper_dict[key] = helper

    return list(helper_dict.values())
