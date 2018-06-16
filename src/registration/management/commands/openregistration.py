from django.core.management.base import BaseCommand, CommandError
from registration.models import Event


class Command(BaseCommand):
    help = 'Opens the registration for the specified events'

    def add_arguments(self, parser):
        parser.add_argument('event_url_name', nargs='+', type=str)

    def handle(self, *args, **options):
        for event_url_name in options['event_url_name']:
            # get event
            try:
                event = Event.objects.get(url_name=event_url_name)
            except Event.DoesNotExist:
                raise CommandError('Event "%s" does not exist' %
                                   event_url_name)

            # open event
            event.active = True
            event.save()

            self.stdout.write('Registration for event "%s" is open now' %
                              event_url_name)
