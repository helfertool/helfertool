from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
import os


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
            return self.event
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
