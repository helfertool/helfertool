from django.db import models
from django.contrib.auth.models import User
from registration.models import Event, Helper

def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]

class HelfertoolLogEntry(models.Model):
    """ Backbone for HelfertoolDatabaseHandler

    Columns:
        :level: Loglevel
        :message: Message of the log
        :time: time of the log
        :app: sender
        :event: the Event used
        :user: the logged in User that emitted the event that created the log
        :helper: the helper referred to in the log
        :extra: any superfluous, generic data stored as json.
    """

    class Meta:
        ordering: ['time']

    level = models.CharField(max_length=16)

    message = models.CharField(max_length=512)

    time = models.DateTimeField(auto_now_add=True)

    app = models.CharField(max_length=128)

    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.CASCADE)

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET(get_sentinel_user))

    helper = models.ForeignKey(Helper, null=True, blank=True, on_delete=models.CASCADE)

    # TODO: Update to Django 3.1 for JSONField:
    # https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield
    extra = models.TextField(blank=True, null=True)
