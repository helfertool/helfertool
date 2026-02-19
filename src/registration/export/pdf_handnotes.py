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


def full_table_of_helpers(elements, helpers, event):
    # table
    header = [par(_("Name")), par(_("Mobile phone"))]
    spaces = [
        5,
        3,
    ]
    if event.ask_shirt:
        header.append(par(_("T-shirt")))
        spaces.append(2.5)
    header.append(par(_("Comment")))
    spaces.append(17 - sum(spaces))  # 17cm are the total possible width, adjust the comment column to fill that

    data = [
        header,
    ]
    data_sets = {}

    for helper in helpers:
        name = "%s %s" % (helper.firstname, helper.surname)
        mobile = helper.phone

        if event.ask_shirt:
            helper_key = (name, mobile, helper.get_shirt_display())
        else:
            helper_key = (name, mobile)

        if helper_key in data_sets.keys():
            data_sets[helper_key] = data_sets[helper_key] + " | " + helper.comment
        else:
            data_sets[helper_key] = helper.comment

    for key, comment in data_sets.items():
        if event.ask_shirt:
            name, mobile, shirt = key
        else:
            name, mobile = key

        tmp = [par(name), par(mobile)]
        if event.ask_shirt:
            tmp.append(par(shirt))
        tmp.append(par(comment))
        data.append(tmp)

    spaces = [s * cm for s in spaces]
    add_table(elements, data, spaces)


def table_of_helper_slots(elements, registered_helpers, number_of_shifts, all_helpers):
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


def pdf_handnotes(buffer, event, jobs, date):
    doc = SimpleDocTemplate(buffer, topMargin=margin, rightMargin=margin, bottomMargin=margin, leftMargin=margin)
    doc.pagesize = A4

    # elements
    elements = []
    # helper information
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

            table_of_helper_slots(elements, coordinators, len(coordinators), all_helpers)

        # iterate over shifts
        for shift in job.shift_set.all():
            if date and shift.date() != date:
                continue

            heading = h2(shift.name)
            elements.append(heading)

            date_str = par(shift.time_with_day())
            elements.append(date_str)

            table_of_helper_slots(elements, shift.helper_set.all(), shift.number, all_helpers)

        # page break
        elements.append(PageBreak())

    elements.append(h1(_("Helper data")))
    full_table_of_helpers(elements, sorted(all_helpers, key=lambda h: (h.firstname, h.surname)), event)

    # build pdf
    doc.build(elements)
