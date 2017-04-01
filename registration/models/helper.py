from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

import uuid

from badges.models import Badge
from gifts.models import HelpersGifts

from .event import Event
from .job import Job


class Helper(models.Model):
    """ Helper in one or more shifts.

    Columns:
        :shifts: all shifts of this person
        :firstname: the firstname
        :surname: the surname
        :email: the e-mail address
        :phone: phone number
        :comment: optional comment
        :shirt: t-shirt size (possible sizes are defined here)
        :vegetarian: is the helper vegetarian?
        :infection_instruction: status of the instruction for food handling
        :timestamp: time of registration
        :validated: the validation link was clicked (if validation is enabled)
    """

    INSTRUCTION_NO = "No"
    INSTRUCTION_YES = "Yes"
    INSTRUCTION_REFRESH = "Refresh"

    INSTRUCTION_CHOICES = (
        (INSTRUCTION_NO, _("I never got an instruction")),
        (INSTRUCTION_YES, _("I have a valid instruction")),
        (INSTRUCTION_REFRESH, _("I got a instruction by a doctor, "
                                "it must be refreshed"))
    )

    INSTRUCTION_CHOICES_SHORT = (
        (INSTRUCTION_NO, _("No")),
        (INSTRUCTION_YES, _("Valid")),
        (INSTRUCTION_REFRESH, _("Refreshment"))
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    shifts = models.ManyToManyField(
        'Shift',
    )

    event = models.ForeignKey(
        'Event',
    )

    firstname = models.CharField(
        max_length=200,
        verbose_name=_("First name"),
    )

    surname = models.CharField(
        max_length=200,
        verbose_name=_("Surname"),
    )

    email = models.EmailField(
        verbose_name=_("E-Mail"),
    )

    phone = models.CharField(
        max_length=200,
        verbose_name=_("Mobile phone"),
    )

    comment = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Comment"),
    )

    shirt = models.CharField(
        max_length=20,
        choices=Event.SHIRT_CHOICES,
        default=Event.SHIRT_UNKNOWN, verbose_name=_("T-shirt"),
    )

    vegetarian = models.BooleanField(
        default=False,
        verbose_name=_("Vegetarian"),
        help_text=_("This helps us estimating the food for our helpers."),
    )

    infection_instruction = models.CharField(
        max_length=20,
        choices=INSTRUCTION_CHOICES,
        blank=True,
        verbose_name=_("Instruction for the handling of food"),
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    validated = models.BooleanField(
        default=True,
        verbose_name=_("E-Mail address was confirmed"),
    )

    privacy_statement = models.BooleanField(
        default=False,
        verbose_name=_("I agree with the following data privacy statement."),
    )

    def __str__(self):
        return "%s %s" % (self.firstname, self.surname)

    def get_infection_instruction_short(self):
        """ Returns the short description for the infection_instruction
            field.
        """
        for item in Helper.INSTRUCTION_CHOICES_SHORT:
            if item[0] == self.infection_instruction:
                return item[1]
        return ""

    @property
    def needs_infection_instruction(self):
        # check shifts
        for shift in self.shifts.all():
            if shift.job.infection_instruction:
                return True

        # check coordinated jobs
        for job in self.coordinated_jobs:
            if job.infection_instruction:
                return True

        return False

    def can_edit(self, user):
        # for helpers
        for shift in self.shifts.all():
            if shift.job.is_admin(user):
                return True

        # for coordinators
        for job in self.job_set.all():
            if job.is_admin(user):
                return True

        return False

    def send_mail(self, request, internal):
        """ Send a confirmation e-mail to the registered helper.

        This e-mail contains a list of the shifts, the helper registered for.
        """
        if self.shifts.count() == 0 and not self.is_coordinator:
            return

        event = self.event
        validate_url = request.build_absolute_uri(reverse('validate',
                                                          args=[event.url_name,
                                                                self.id]))
        registered_url = request.build_absolute_uri(reverse('registered',
                                                    args=[event.url_name,
                                                          self.id]))

        subject_template = get_template('registration/mail/subject.txt')
        subject = subject_template.render({'event': event}).rstrip()

        if self.is_coordinator:
            text_template = get_template('registration/mail/coordinator.txt')
        elif internal:
            text_template = get_template('registration/mail/internal.txt')
        else:
            text_template = get_template('registration/mail/public.txt')
        text = text_template.render({'user': self,
                                     'event': event,
                                     'validate_url': validate_url,
                                     'registered_url': registered_url})

        mail = EmailMessage(subject,
                            text,
                            settings.FROM_MAIL,
                            [self.email, ],  # to
                            reply_to=[event.email, ])

        mail.send(fail_silently=False)

    def check_delete(self):
        if self.shifts.count() == 0 and not self.is_coordinator:
            self.delete()

    @property
    def full_name(self):
        """ Returns full name of helper """
        return "%s %s" % (self.firstname, self.surname)

    @property
    def has_to_validate(self):
        if not self.event:
            return False

        return self.event.mail_validation and not self.validated

    @property
    def coordinated_jobs(self):
        if hasattr(self, 'job_set'):
            return getattr(self, 'job_set').all()
        return []

    @property
    def is_coordinator(self):
        if not hasattr(self, 'job_set'):
            return False
        return getattr(self, 'job_set').count() > 0

    @property
    def first_shift(self):
        shifts = self.shifts.order_by('begin')
        if len(shifts) > 0:
            return shifts[0]
        return None


@receiver(post_save, sender=Helper, dispatch_uid='helper_saved')
def helper_saved(sender, instance, using, **kwargs):
    """ Add badge and gifts to helper if necessary.

    This is a signal handler, that is called, when a helper is saved. It
    adds the badge if badge creation is enabled and it is not there already.
    """
    if instance.event:
        if instance.event.badges and not hasattr(instance, 'badge'):
            badge = Badge()
            badge.helper = instance
            badge.save()

        if instance.event.gifts and not hasattr(instance, 'gifts'):
            gifts = HelpersGifts()
            gifts.helper = instance
            gifts.save()


def helper_deleted(sender, **kwargs):
    action = kwargs.pop('action')

    if action == "post_remove":
        helper = kwargs.pop('instance')
        helper.check_delete()


def coordinator_deleted(sender, **kwargs):
    action = kwargs.pop('action')
    instance = kwargs.pop('instance')

    if action == "post_remove":
        pk_set = kwargs.pop('pk_set')
        model = kwargs.pop('model')  # this is Helper

        # iterate over all deleted helpers, this should be only one helper
        for helper_pk in pk_set:
            helper = model.objects.get(pk=helper_pk)
            helper.check_delete()

m2m_changed.connect(helper_deleted, sender=Helper.shifts.through)
m2m_changed.connect(coordinator_deleted, sender=Job.coordinators.through)
