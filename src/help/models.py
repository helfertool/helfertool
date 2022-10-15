from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class Issue(models.Model):
    NEW_EVENT = "newevent"
    PROMOTE_EVENT = "promoteevent"
    PERM_ADD_USER = "permadduser"
    PERM_ADD_EVENT = "permaddevent"
    FEATURE = "feature"
    BUG = "bug"
    OTHER = "other"

    SUBJECT_CHOICES = (
        (NEW_EVENT, _("New event")),
        (PROMOTE_EVENT, _("Promote event")),
        (PERM_ADD_USER, _("Permission to add new users")),
        (PERM_ADD_EVENT, _("Permission to add new events")),
        (FEATURE, _("Feature request")),
        (BUG, _("Bug report")),
        (OTHER, _("Other topic")),
    )

    sender = models.ForeignKey(
        get_user_model(),
        null=True,
        on_delete=models.SET_NULL,
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )

    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES,
        verbose_name=_("Topic"),
    )

    text = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Text"),
    )

    done_by = models.ForeignKey(
        get_user_model(),
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return "{}: {}".format(self.sender.get_full_name(), self.get_subject_display())
