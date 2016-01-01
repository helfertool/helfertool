from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
import posixpath

from .defaults import BadgeDefaults


def _settings_upload_path(instance, filename):
    event = str(instance.event.pk)

    return posixpath.join('badges', event, 'template', filename)


class BadgeSettings(models.Model):
    """ Settings for badge creation

    Columns:
        :event: The event that uses the badge creation
    """

    event = models.OneToOneField(
        'registration.Event'
    )

    defaults = models.OneToOneField(
        'BadgeDefaults'
    )

    latex_template = models.FileField(
        verbose_name=_("LaTeX template"),
        upload_to=_settings_upload_path,
        null=True,
    )

    rows = models.IntegerField(
        default=5,
        verbose_name=_("Number of rows on one page"),
        validators=[MinValueValidator(1)],
    )

    columns = models.IntegerField(
        default=2,
        verbose_name=_("Number of columns on one page"),
        validators=[MinValueValidator(1)],
    )

    barcodes = models.BooleanField(
        default=False,
        verbose_name=_("Print barcodes on badges to avoid duplicates"),
    )

    coordinator_title = models.CharField(
        max_length=200,
        default="",
        verbose_name=_("Role for coordinators"),
    )

    helper_title = models.CharField(
        max_length=200,
        default="",
        verbose_name=_("Role for helpers"),
    )

    def save(self, *args, **kwargs):
        if not hasattr(self, 'defaults'):
            defaults = BadgeDefaults()
            defaults.save()

            self.defaults = defaults

        super(BadgeSettings, self).save(*args, **kwargs)

    def creation_possible(self):
        if not self.latex_template:
            return False

        if not self.defaults.role:
            return False

        if not self.defaults.design:
            return False

        return True
