from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import posixpath
from copy import deepcopy

from .settings import BadgeSettings


def _design_upload_path(instance, filename):
    event = str(instance.get_event().pk)

    return posixpath.join('badges', event, 'backgrounds', filename)


@python_2_unicode_compatible
class BadgeDesign(models.Model):
    """ Design of a badge (for an event or job)

    Columns:
        :badge_settings: settings
        :name: name of design
        :font_color: Color of the text
        :bg_front: Background picture of the front
        :bg_back: Background picture of the back
    """

    def get_event(self):
        return self.badge_settings.event

    badge_settings = models.ForeignKey(
        BadgeSettings,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    font_color = models.CharField(
        max_length=7,
        default="#000000",
        validators=[RegexValidator('^#[a-fA-F0-9]{6}$')],
        verbose_name=_("Color for text"),
        help_text=_("E.g. #00ff00"),
    )

    bg_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        validators=[RegexValidator('^#[a-fA-F0-9]{6}$')],
        verbose_name=_("Background color"),
        help_text=_("E.g. #00ff00"),
    )

    bg_front = models.ImageField(
        verbose_name=_("Background image for front"),
        upload_to=_design_upload_path,
        blank=True,
        null=True,
    )

    bg_back = models.ImageField(
        verbose_name=_("Background image for back"),
        upload_to=_design_upload_path,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    def duplicate(self, settings):
        new_design = deepcopy(self)

        new_design.pk = None
        new_design.badge_settings = settings

        new_design.save()

        return new_design

        # TODO: bg_fron, bg_back
