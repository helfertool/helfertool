from django.core.management.base import BaseCommand
from registration.models import Helper


class Command(BaseCommand):
    help = 'Checks for helpers that have no shift and are not coordinators'

    def handle(self, *args, **options):
        for helper in Helper.objects.all():
            if helper.shifts.count() == 0 and not helper.is_coordinator:
                self.stdout.write(str(helper.id))
