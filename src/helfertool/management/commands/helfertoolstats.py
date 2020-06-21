from django.core.management.base import BaseCommand
from django.db.models import Sum

from registration.models import Event, Job, Shift, Helper


class Command(BaseCommand):
    help = 'Print number of events, jobs, shifts and helpers'

    def handle(self, *args, **options):
        events = Event.objects.count()
        jobs = Job.objects.count()
        shifts = Shift.objects.count()
        helpers = Helper.objects.count()

        helpers_archived = Shift.objects.filter(archived_number__isnull=False) \
            .aggregate(total=Sum('archived_number'))['total']
        if helpers_archived:
            helpers += helpers_archived

        print("Events:\t\t{}".format(events))
        print("Jobs:\t\t{}".format(jobs))
        print("Shifts:\t\t{}".format(shifts))
        print("Helpers:\t{}".format(helpers))
