import csv
from django.utils import timezone


def csv_export(buffer, event, jobs, date, include_sensitive, included_columns):
    """Exports the helpers for given jobs of an event as csv.

    Parameter:
        buffer: a writeable bytes buffer (e.g. io.BytesIO or a file)
        event:  the exported event
        jobs:   a list of all exported jobs
        date:   export only for this date
        include_sensitive: Include sensitive data in export
        included_columns: columns to include in the export {column_name: bool_include}
    """
    fieldnames = [
        "job",
        "start",
        "end",
        "shift",
        "firstname",
        "lastname",
        "email",
        "phone",
        "shirt",
        "nutrition",
        "foodhandling",
        "comment",
    ]

    csv_writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
    )
    csv_writer.writeheader()

    # create list of dicts
    for job in jobs:
        included_columns["phone"] = event.ask_phone and included_columns["phone"] and include_sensitive
        included_columns["shirt"] = event.ask_shirt and included_columns["shirt"]
        included_columns["nutrition"] = event.ask_nutrition and included_columns["nutrition"]
        included_columns["foodhandling"] = job.infection_instruction and included_columns["foodhandling"]

        for shift in job.shift_set.order_by("begin"):
            if date and shift.date() != date:
                continue

            add_helpers(csv_writer, job, shift.helper_set.all(), included_columns, shift)


def add_helpers(csv_writer, job, helpers, included_columns, shift):
    # empty shifts
    empty_shifts = shift.number - len(helpers)

    start = timezone.localtime(shift.begin).isoformat()
    end = timezone.localtime(shift.end).isoformat()

    for helper in helpers:
        # num_shifts = helper.shifts.count()
        # num_jobs = len(helper.coordinated_jobs)
        column = {}

        if included_columns["name"]:
            column["firstname"] = helper.firstname
            column["lastname"] = helper.surname
        if included_columns["email"]:
            column["email"] = helper.email
        if included_columns["phone"]:
            column["phone"] = helper.phone
        if included_columns["shirt"]:
            column["shirt"] = str(helper.get_shirt_display())
        if included_columns["nutrition"]:
            column["nutrition"] = str(helper.get_nutrition_short())
        if included_columns["foodhandling"]:
            column["foodhandling"] = str(helper.get_infection_instruction_short())
        if included_columns["comment"]:
            column["comment"] = helper.comment

        column["job"] = job.name
        # column["start"] = shift.begin.strftime("%Y-%m-%d %H:%M")
        # column["end"] = shift.end.strftime("%Y-%m-%d %H:%M")
        # iso with timezone
        column["start"] = start
        column["end"] = end
        column["shift"] = shift.name

        csv_writer.writerow(column)
    for _ in range(empty_shifts):
        column = {
            "job": job.name,
            "start": start,
            "end": end,
            "shift": shift.name,
        }

        csv_writer.writerow(column)
