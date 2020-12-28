from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    name = 'registration'

#    def ready(self):
#        from . import tasks
#        tasks.setup_event_flags.delay()
