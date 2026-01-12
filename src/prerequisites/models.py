from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prose_editor.fields import ProseEditorField
from helfertool.utils import PROSE_EDITOR_DEFAULT_EXTENSIONS

from copy import deepcopy


class Prerequisite(models.Model):
    """
    Prerequisite for one or many jobs

    Columns:
        :name: Name
        :description: Description
        :helper_can_set: Helpers can specify at registration whether they have this prerequisite
    """

    event = models.ForeignKey(
        "registration.Event",
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    description = ProseEditorField(
        extensions=PROSE_EDITOR_DEFAULT_EXTENSIONS,
        sanitize=True,
        blank=True,
        verbose_name=_("Description"),
    )

    def check_helper(self, helper):
        """
        Checks whether helper fulfills this prerequisite or not.

        Returns bool.
        """
        if self.event != helper.event:
            raise ValueError("Helper and requirement do not belong to same event")

        try:
            fulfilled = FulfilledPrerequisite.objects.get(prerequisite=self, helper=helper)
            return fulfilled.has_prerequisite
        except FulfilledPrerequisite.DoesNotExist:
            return False

    def set_helper(self, helper, state):
        """
        Change state, whether helper fulfills this prerequisite or not.
        """
        if self.event != helper.event:
            raise ValueError("Helper and requirement do not belong to same event")

        try:
            fulfilled = FulfilledPrerequisite.objects.get(prerequisite=self, helper=helper)
            fulfilled.has_prerequisite = state
            fulfilled.save()
        except FulfilledPrerequisite.DoesNotExist:
            FulfilledPrerequisite.objects.create(prerequisite=self, helper=helper, has_prerequisite=state)

    def duplicate(self, event):
        new_prerequisite = deepcopy(self)
        new_prerequisite.pk = None
        new_prerequisite.event = event
        new_prerequisite.save()

        return new_prerequisite

    def __str__(self):
        return self.name


class FulfilledPrerequisite(models.Model):
    """
    Link between helpers and prerequisites

    Columns:
        :has_prerequisite: The helper fulfils this prerequisite
    """

    prerequisite = models.ForeignKey(
        "prerequisites.Prerequisite",
        on_delete=models.CASCADE,
    )

    helper = models.ForeignKey(
        "registration.Helper",
        on_delete=models.CASCADE,
    )

    has_prerequisite = models.BooleanField(
        default=False,
        verbose_name=_("Helper fulfils this prerequisite"),
    )

    def __str__(self):
        return "{} - {}".format(self.prerequisite, self.helper)
