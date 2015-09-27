from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import uuid

from .badge import Badge


@python_2_unicode_compatible
class Helper(models.Model):
    """ Helper in one or more shifts.

    Columns:
        :shifts: all shifts of this person
        :prename: the prename
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

    SHIRT_S = 'S'
    SHIRT_M = 'M'
    SHIRT_L = 'L'
    SHIRT_XL = 'XL'
    SHIRT_XXL = 'XXL'
    SHIRT_S_GIRLY = 'S_GIRLY'
    SHIRT_M_GIRLY = 'M_GIRLY'
    SHIRT_L_GIRLY = 'L_GIRLY'
    SHIRT_XL_GIRLY = 'XL_GIRLY'

    SHIRT_CHOICES = (
        (SHIRT_S, 'S'),
        (SHIRT_M, 'M'),
        (SHIRT_L, 'L'),
        (SHIRT_XL, 'XL'),
        (SHIRT_XXL, 'XXL'),
        (SHIRT_S_GIRLY, 'S (girly)'),
        (SHIRT_M_GIRLY, 'M (girly)'),
        (SHIRT_L_GIRLY, 'L (girly)'),
        (SHIRT_XL_GIRLY, 'XL (girly)'),
    )

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

    prename = models.CharField(
        max_length=200,
        verbose_name=_("Prename"),
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
        choices=SHIRT_CHOICES,
        default=SHIRT_S, verbose_name=_("T-shirt"),
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

    def __str__(self):
        return "%s %s" % (self.prename, self.surname)

    def get_infection_instruction_short(self):
        """ Returns the short description for the infection_instruction
            field.
        """
        for item in Helper.INSTRUCTION_CHOICES_SHORT:
            if item[0] == self.infection_instruction:
                return item[1]
        return ""

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

    def send_mail(self, request):
        """ Send a confirmation e-mail to the registered helper.

        This e-mail contains a list of the shifts, the helper registered for.
        """
        if self.shifts.count() == 0:
            return

        event = self.event
        validate_url = request.build_absolute_uri(reverse('validate',
                                                          args=[event.url_name,
                                                                self.id]))

        subject_template = get_template('registration/mail_subject.txt')
        subject = subject_template.render({'event': event}).rstrip()

        text_template = get_template('registration/mail.txt')
        text = text_template.render({'user': self,
                                     'event': event,
                                     'validate_url': validate_url})

        send_mail(subject, text, event.email, [self.email],
                  fail_silently=False)

    @property
    def event(self):
        """ Returns the event, where this person helps us.

        If the helper is not registered for any shift, None is returned (this
        should not happen).
        """

        if self.shifts.count() == 0:
            return None

        return self.shifts.all()[0].job.event

    @property
    def full_name(self):
        """ Returns full name of helper """
        return "%s %s" % (self.prename, self.surname)

    @property
    def has_to_validate(self):
        event = self.event

        if not event:
            return False

        return event.mail_validation and not self.validated

@receiver(post_save, sender=Helper, dispatch_uid='helper_saved')
def helper_saved(sender, instance, using, **kwargs):
    """ Add badge to helper if necessary.

    This is a signal handler, that is called, when a helper is saved. It
    adds the badge if badge creation is enabled and it is not there already.
    """
    if instance.event.badges and not hasattr(instance, 'badge'):
        badge = Badge()
        badge.helper = instance
        badge.save()
