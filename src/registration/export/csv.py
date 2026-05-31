import csv
from django.utils import timezone


def csv_export(buffer, event, jobs, date):
    """Exports the helpers for given jobs of an event as csv.

    Parameter:
        buffer: a writeable bytes buffer (e.g. io.BytesIO or a file)
        event:  the exported event
        jobs:   a list of all exported jobs
        date:   export only for this date
    """
    fieldnames = [
        "job",
        "start",
        "end",
        "shift",
        "firstname",
        "lastname",
    ]

    csv_writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
    )
    csv_writer.writeheader()

    # create list of dicts
    for job in jobs:
        for shift in job.shift_set.order_by("begin"):
            if date and shift.date() != date:
                continue

            add_helpers(csv_writer, job, shift.helper_set.all(), shift)


def add_helpers(csv_writer, job, helpers, shift):
    empty_shifts = shift.number - len(helpers)

    start = timezone.localtime(shift.begin).isoformat()
    end = timezone.localtime(shift.end).isoformat()

    for helper in helpers:
        column = {}
        column["job"] = job.name
        column["start"] = start
        column["end"] = end
        column["shift"] = shift.name
        column["firstname"] = helper.firstname
        column["lastname"] = helper.surname

        csv_writer.writerow(column)
    for _ in range(empty_shifts):
        column = {
            "job": job.name,
            "start": start,
            "end": end,
            "shift": shift.name,
        }

        csv_writer.writerow(column)
