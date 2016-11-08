from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Issue(models.Model):
    NEW_EVENT = 'newevent'
    PERM_ADD_USER = 'permadduser'
    PERM_ADD_EVENT = 'permaddevent'
    FEATURE = 'feature'
    BUG = 'bug'
    OTHER = 'other'

    SUBJECT_CHOICES = (
        (NEW_EVENT, _("New event")),
        (PERM_ADD_USER, _("Permission to add new users")),
        (PERM_ADD_EVENT, _("Permission to add new events")),
        (FEATURE, _("Feature request")),
        (BUG, _("Bug report")),
        (OTHER, _("Other topic")),
    )

    sender = models.ForeignKey(
        User,
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )

    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES,
        verbose_name=_("Subject"),
    )

    text = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Text"),
    )

    done_by = models.ForeignKey(
        User,
        null=True,
        related_name='+',
    )

    def __str__(self):
        return "{}: {}".format(self.sender.get_full_name(),
                               self.get_subject_display())
