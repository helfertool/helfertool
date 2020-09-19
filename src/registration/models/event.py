from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_bleach.models import BleachField
from multiselectfield import MultiSelectField

import datetime

from badges.models import BadgeSettings, BadgeDefaults, Badge
from gifts.models import HelpersGifts
from gifts.models.giftsettings import GiftSettings
from inventory.models import InventorySettings


def _default_mail():
    return settings.EMAIL_SENDER_ADDRESS


class Event(models.Model):
    class Meta:
        ordering = ['name', 'url_name']

    """ Event for registration.

    Columns:
        :url_name: the ID of the event used in URLs
        :name: the name of the event
        :text: text at begin of registration
        :imprint: text at the bottom if the registration page
        :registered: text after the successful registration
        :email: e-mail address used as sender of automatic e-mails
        :active: is the registration opened?
        :admins: list of admins of this event, they can see and edit everything
        :ask_shirt: ask for the t-shirt size during registration
        :ask_phone: ask for the mobile phone number during registration
        :ask_vegetarian: ask, if the helper is vegetarian
        :show_public_numbers: show the number of current and maximal helpers on
                             the registration page
        :mail_validation: helper must validate his mail address by a link
        :badge: use the badge creation system
    """

    SHIRT_UNKNOWN = 'UNKNOWN'
    SHIRT_NO = 'NO'
    SHIRT_XS = 'XS'
    SHIRT_S = 'S'
    SHIRT_M = 'M'
    SHIRT_L = 'L'
    SHIRT_XL = 'XL'
    SHIRT_XXL = 'XXL'
    SHIRT_3XL = '3XL'
    SHIRT_XS_GIRLY = 'XS_GIRLY'
    SHIRT_S_GIRLY = 'S_GIRLY'
    SHIRT_M_GIRLY = 'M_GIRLY'
    SHIRT_L_GIRLY = 'L_GIRLY'
    SHIRT_XL_GIRLY = 'XL_GIRLY'
    SHIRT_XXL_GIRLY = 'XXL_GIRLY'

    SHIRT_CHOICES = (
        (SHIRT_UNKNOWN, _('Unknown')),
        (SHIRT_NO, _('I do not want a T-Shirt')),
        (SHIRT_XS, _('XS')),
        (SHIRT_S, _('S')),
        (SHIRT_M, _('M')),
        (SHIRT_L, _('L')),
        (SHIRT_XL, _('XL')),
        (SHIRT_XXL, _('XXL')),
        (SHIRT_3XL, _('3XL')),
        (SHIRT_XS_GIRLY, _('XS (girly)')),
        (SHIRT_S_GIRLY, _('S (girly)')),
        (SHIRT_M_GIRLY, _('M (girly)')),
        (SHIRT_L_GIRLY, _('L (girly)')),
        (SHIRT_XL_GIRLY, _('XL (girly)')),
        (SHIRT_XXL_GIRLY, _('XXL (girly)')),
    )

    SHIRT_CHOICES_DEFAULTS = (
        SHIRT_S,
        SHIRT_M,
        SHIRT_L,
        SHIRT_XL,
        SHIRT_XXL,
        SHIRT_S_GIRLY,
        SHIRT_M_GIRLY,
        SHIRT_L_GIRLY,
        SHIRT_XL_GIRLY,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Event name"),
    )

    url_name = models.CharField(
        max_length=200,
        unique=True,
        validators=[RegexValidator('^[a-zA-Z0-9]+$')],
        verbose_name=_("Name for URL"),
        help_text=_("May contain the following chars: a-zA-Z0-9."),
    )

    date = models.DateField(
        verbose_name=_("Date"),
        help_text=_("First day of event"),
    )

    days = models.IntegerField(
        default=1,
        verbose_name=_("Number of days"),
        help_text=_("Displayed on the main page"),
        validators=[MinValueValidator(0)],
    )

    text = BleachField(
        blank=True,
        verbose_name=_("Text before registration"),
        help_text=_("Displayed as first text of the registration form."),
    )

    imprint = BleachField(
        blank=True,
        verbose_name=_('Contact'),
        help_text=_("Displayed at the bottom of all pages for the event."),
    )

    registered = BleachField(
        blank=True,
        verbose_name=_("Text after registration"),
        help_text=_("Displayed after registration."),
    )

    email = models.EmailField(
        default=_default_mail,
        verbose_name=_("E-Mail"),
        help_text=_("Used as Reply-to address for mails sent to helpers"),
    )

    # note: there is code to duplicate the file in forms/event.py
    logo = models.ImageField(
        upload_to='logos',
        blank=True,
        null=True,
        verbose_name=_("Logo"),
    )

    # note: there is code to duplicate the file in forms/event.py
    logo_social = models.ImageField(
        upload_to='logos',
        blank=True,
        null=True,
        verbose_name=_("Logo for Facebook"),
        help_text=_("Best results with 1052 x 548 px."),
    )

    max_overlapping = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maximal overlapping of shifts"),
        help_text=_("If two shifts overlap more than this value in minutes "
                    "it is not possible to register for both shifts. Leave "
                    "empty to disable this check."),
    )

    admins = models.ManyToManyField(
        get_user_model(),
        blank=True,
        through='registration.EventAdminRoles'
    )

    active = models.BooleanField(
        default=False,
        verbose_name=_("Registration publicly visible"),
    )

    changes_until = models.DateField(
        verbose_name=_("Deregistration and changes possible until"),
        help_text=_("Helpers can change their personal data and shifts until "
                    "this date themselves. Leave emtpy to disable this."),
        null=True,
        blank=True,
    )

    ask_phone = models.BooleanField(
        default=True,
        verbose_name=_("Ask for phone number"),
    )

    ask_shirt = models.BooleanField(
        default=True,
        verbose_name=_("Ask for T-shirt size"),
    )

    ask_vegetarian = models.BooleanField(
        default=True,
        verbose_name=_("Ask, if helper is vegetarian"),
    )

    ask_full_age = models.BooleanField(
        default=True,
        verbose_name=_("Helpers have to confirm to be full age")
    )

    ask_news = models.BooleanField(
        default=True,
        verbose_name=_("Ask if helper wants to be notified about new events"),
    )

    show_public_numbers = models.BooleanField(
        default=True,
        verbose_name=_("Show number of helpers on registration page"),
    )

    mail_validation = models.BooleanField(
        default=True,
        verbose_name=_("Registrations for public shifts must be validated by "
                       "a link that is sent per mail"),
    )

    badges = models.BooleanField(
        default=False,
        verbose_name=_("Use badge creation"),
    )

    gifts = models.BooleanField(
        default=False,
        verbose_name=_("Manage gifts for helpers"),
    )

    inventory = models.BooleanField(
        default=False,
        verbose_name=_("Use the inventory functionality"),
    )

    prerequisites = models.BooleanField(
        default=False,
        verbose_name=_("Manage prerequisites for helpers"),
    )

    archived = models.BooleanField(
        default=False,
        verbose_name=_("Event is archived"),
    )

    shirt_sizes = MultiSelectField(
        choices=filter(lambda e: e[0] != 'UNKNOWN', SHIRT_CHOICES),
        default=SHIRT_CHOICES_DEFAULTS,
        max_length=250,
        verbose_name=_("Available T-shirt sizes"),
    )

    def __str__(self):
        return self.name

    def clean(self):
        # the shirt sizes of the helpers must be selected in shirt_sizes
        # this means that it is not possible to disable a size as long one
        # helper has selected this size
        if self.ask_shirt:
            not_removable = []

            new_choices = self.get_shirt_choices()
            for choice in Event.SHIRT_CHOICES:
                if choice not in new_choices and self.helper_set.filter(shirt=choice[0]).exists():
                    not_removable.append(choice[1])

            if not_removable:
                sizes = ', '.join(map(str, not_removable))
                raise ValidationError({'shirt_sizes':
                                       _("The following sizes are used and "
                                         "therefore cannot be removed: {}".
                                         format(sizes))})

    def get_shirt_choices(self, internal=True):
        choices = []

        for shirt in Event.SHIRT_CHOICES:
            if (shirt[0] == Event.SHIRT_UNKNOWN and internal) or \
                    shirt[0] in self.shirt_sizes:
                choices.append(shirt)

        return choices

    @property
    def public_jobs(self):
        return self.job_set.filter(public=True)

    @property
    def badge_settings(self):
        try:
            return self.badgesettings
        except AttributeError:
            return None

    @property
    def inventory_settings(self):
        try:
            return self.inventorysettings
        except AttributeError:
            return None

    @property
    def gift_settings(self):
        try:
            return self.giftsettings
        except AttributeError:
            return None

    @property
    def all_coordinators(self):
        return self.helper_set.filter(job__isnull=False)

    @property
    def changes_possible(self):
        return self.changes_until is not None and \
            datetime.date.today() <= self.changes_until


@receiver(post_save, sender=Event, dispatch_uid='event_saved')
def event_saved(sender, instance, using, **kwargs):
    """ Add badge settings, badges and gifts if necessary.

    This is a signal handler, that is called, when a event is saved. It
    adds the badge settings if badge creation is enabled and it is not
    there already. It also adds badge defaults to all jobs and badges to all
    helpers and coordinators if necessary.
    """
    if instance.badges:
        _setup_badge_settings(instance)

    if instance.gifts:
        _setup_gift_settings(instance)

    if instance.inventory:
        _setup_inventory_settings(instance)


def _setup_badge_settings(event):
    """
    Set up badges for all jobs and helpers
    """
    # badge settings for event
    if not event.badge_settings:
        settings = BadgeSettings()
        settings.event = event
        settings.save()

    # badge defaults for jobs
    for job in event.job_set.all():
        if not job.badge_defaults:
            defaults = BadgeDefaults()
            defaults.save()

            job.badge_defaults = defaults
            job.save()

    # badge for helpers
    for helper in event.helper_set.all():
        if not hasattr(helper, 'badge'):
            badge = Badge()
            badge.event = event
            badge.helper = helper
            badge.save()


def _setup_gift_settings(event):
    """
    Setup gift relations for all helpers
    """
    if not event.gift_settings:
        GiftSettings.objects.create(event=event)

    for helper in event.helper_set.all():
        if not hasattr(helper, 'gifts'):
            gifts = HelpersGifts()
            gifts.helper = helper
            gifts.save()


def _setup_inventory_settings(event):
    if not event.inventory_settings:
        InventorySettings.objects.create(event=event)
