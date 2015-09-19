from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import os


class BadgeSettings(models.Model):
    """ Settings for badge creation

    Columns:
        :event: The event that uses the badge creation
        :badge_design: Default badge design
    """

    def upload_path(instance, filename):
        event = str(instance.event.pk)

        path = os.path.join(settings.BADGE_IMAGE_DIR, event, 'template.tex')

        return path

    event = models.OneToOneField(
        'Event'
    )

    design = models.OneToOneField(
        'BadgeDesign',
    )

    latex_template = models.FileField(
        verbose_name=_("LaTeX template"),
        upload_to=upload_path,
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

    def save(self, *args, **kwargs):
        if not hasattr(self, 'design'):
            design = BadgeDesign()
            design.save()

            self.design = design

        super(BadgeSettings, self).save(*args, **kwargs)


class BadgeDesign(models.Model):
    """ Design of a badge (for an event or job)

    Columns:
        :font_color: Color of the text
        :bg_front: Background picture of the front
        :bg_back: Background picture of the back
    """

    def upload_path(instance, filename):
        event = str(instance.get_event().pk)

        path = os.path.join(settings.BADGE_IMAGE_DIR, event, filename)

        # check is file already exists -> add number
        counter = 0
        while os.path.isfile(path) or os.path.isdir(path):
            counter = counter + 1
            path = os.path.join(settings.BADGE_IMAGE_DIR, event,
                                "%d%s" % (counter, filename))

        return path

    def get_event(self):
        try:
            return self.badgesettings.event
        except AttributeError:
            return self.job.event

    font_color = models.CharField(
        max_length=7,
        default="#000000",
        validators=[RegexValidator('^#[a-fA-F0-9]{6}$')],
        verbose_name=_("Color for text"),
        help_text=_("E.g. #00ff00"),
    )

    bg_front = models.ImageField(
        verbose_name=_("Background image for front"),
        upload_to=upload_path,
    )

    bg_back = models.ImageField(
        verbose_name=_("Background image for back"),
        upload_to=upload_path,
    )
