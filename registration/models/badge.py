from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import os


class BadgeSettings(models.Model):
    """ Settings for badge creation

    Columns:
        :event: The event that uses the badge creation
    """

    def upload_path(instance, filename):
        event = str(instance.event.pk)

        path = os.path.join(settings.BADGE_IMAGE_DIR, event, 'template.tex')

        return path

    event = models.OneToOneField(
        'Event'
    )

    defaults = models.OneToOneField(
        'BadgeDefaults'
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
        if not hasattr(self, 'defaults'):
            defaults = BadgeDefaults()
            defaults.save()

            self.defaults = defaults

        super(BadgeSettings, self).save(*args, **kwargs)


class BadgeDefaults(models.Model):
    role = models.ForeignKey(
        'BadgeRole',
        related_name='+',  # no reverse accessor
        null=True,
        blank=True,
        verbose_name=_("Default role"),
    )

    design = models.ForeignKey(
        'BadgeDesign',
        related_name='+',  # no reverse accessor
        null=True,
        blank=True,
        verbose_name=_("Default design"),
    )


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

    bg_front = models.ImageField(
        verbose_name=_("Background image for front"),
        upload_to=upload_path,
    )

    bg_back = models.ImageField(
        verbose_name=_("Background image for back"),
        upload_to=upload_path,
    )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class BadgePermission(models.Model):
    badge_settings = models.ForeignKey(
        BadgeSettings,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    latex_name = models.CharField(
        max_length=200,
        verbose_name=_("Name for LaTeX template"),
        help_text=_("This name is used for the LaTeX template, the prefix "
                    "\"perm-\" is added."),
    )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class BadgeRole(models.Model):
    badge_settings = models.ForeignKey(
        BadgeSettings,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    latex_name = models.CharField(
        max_length=200,
        verbose_name=_("Name for LaTeX template"),
        help_text=_("This name is used for the LaTeX template."),
    )

    permissions = models.ManyToManyField(
        BadgePermission,
        blank=True,
    )

    def __str__(self):
        return self.name


class Badge(models.Model):
    helper = models.OneToOneField(
        'Helper',
    )

    prename = models.CharField(
        max_length=200,
        verbose_name=_("Prename"),
    )

    surname = models.CharField(
        max_length=200,
        verbose_name=_("Surname"),
    )

    job = models.CharField(
        max_length=200,
        verbose_name=_("Job"),
    )

    shift = models.CharField(
        max_length=200,
        verbose_name=_("Shift"),
    )

    role = models.CharField(
        max_length=200,
        verbose_name=_("Role"),
    )
