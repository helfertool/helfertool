from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

import os

from .badge import Badge


def _copy_badge(src, dest):
    """ Copies all data from badge1 to badge2, except for the first and surname. """
    dest.job = src.job
    dest.shift = src.shift
    dest.role = src.role
    dest.custom_role = src.custom_role
    dest.custom_design = src.custom_design

    if src.event == dest.event:
        # same event, reuse the same file
        dest.photo = src.photo
    else:
        # different event, copy the file
        dest.photo = ContentFile(src.photo.read())
        dest.photo.name = os.path.basename(src.photo.name)


class SpecialBadges(models.Model):
    """
    Sometimes, it is necessary to print several (almost) identical badges, for example for the police
    (Police 1, Police 2, etc.). We do not want to create all of them manually and we want to be able
    to change them after creating them (so a bulk-create is not enough).

    This model manages a batch of badges with the same name and a number.

    There is a "template badge" that is edited by the user, the data is then copied to all other badges.
    Most data is copied directly, except of the name:
    * firstname = name from this model
    * surname = incremented number (1, 2, 3, ...)

    The name is not localized as it is just printed on the badge.
    """
    event = models.ForeignKey(
        'registration.Event',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
    )

    number = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Number of badges"),
    )

    # the first badge of the batch. this one is edited by the user and copied afterwards
    # creation and deletion are done in signal handlers
    # it is included in the list of badges (next field)
    template_badge = models.OneToOneField(
        'Badge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    # the Badge objects, which are managed by this special badge
    # we have a one-to-many relation here, but it is cleaner to add it here instead of a foreinkey at the Badge model
    # the template_badge is included here
    badges = models.ManyToManyField(
        'Badge',
        blank=True,
        related_name='+',
    )

    def __str__(self):
        return "{} - {} ({})".format(self.event, self.name, self.number)

    def duplicate(self, event):
        # create new SpecialBadges object and all associated badges
        new_specialbadges = SpecialBadges()
        new_specialbadges.event = event
        new_specialbadges.name = self.name
        new_specialbadges.number = self.number

        new_specialbadges.template_badge = Badge.objects.create(event=event)
        _copy_badge(self.template_badge, new_specialbadges.template_badge)

        new_specialbadges.save()

        return new_specialbadges


@receiver(post_save, sender=SpecialBadges, dispatch_uid='specialbadges_postsave')
def specialbadges_postsave(sender, instance, **kwargs):
    """ After saving a SpecialBadges object, update the batch of badges based on the template badge. """
    # if we do not have a template_badge yet, create it and add it to the badges
    if not instance.template_badge:
        instance.template_badge = Badge.objects.create(event=instance.event)
        instance.save()
        instance.badges.add(instance.template_badge)

    # update name of template badge
    instance.template_badge.firstname = instance.name
    if instance.number > 1:
        instance.template_badge.surname = 1
    else:
        instance.template_badge.surname = ""
    instance.template_badge.save()

    # add or update other badges (2, ...)
    for n in range(2, instance.number+1):
        # get or create badge object
        try:
            badge = instance.badges.get(surname=str(n))
        except Badge.DoesNotExist:
            badge = Badge.objects.create(event=instance.event)
            instance.badges.add(badge)

        # update data
        badge.firstname = instance.name
        badge.surname = str(n)

        _copy_badge(instance.template_badge, badge)

        badge.save()

    # if the number was decreased, we need to delete some badges
    if instance.number < instance.badges.count():
        for n in range(instance.number+1, instance.badges.count()+1):
            Badge.objects.filter(surname=str(n)).delete()


@receiver(pre_delete, sender=SpecialBadges, dispatch_uid='specialbadges_deleted')
def specialbadges_deleted(sender, instance, **kwargs):
    """ When a SpecialBadges object is deleted, delete all managed badges. """
    for badge in instance.badges.all():
        badge.delete()
