from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.template import Context
from django.template.defaultfilters import date as date_filter
from django.template.loader import get_template
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict
import uuid
import smtplib


class Event(models.Model):
    """ Event for registration.

    Columns:
        name: the name of the event
        text: text at begin of registration
        imprint: text at the end of registration
        active: is the registration opened?
    """
    url_name = models.CharField(max_length=200, unique=True,
                                validators=[RegexValidator('^[a-zA-Z0-9]+$')],
                                verbose_name=_("Name for URL"),
                                help_text=_("May contain the following chars: a-zA-Z0-9."))

    name = models.CharField(max_length=200, verbose_name=_("Event name"))

    text = models.TextField(blank=True,
                            verbose_name=_("Text before registration"),
                            help_text=_("Displayed as first text of the registration form."))

    imprint = models.TextField(blank=True, verbose_name=_('Imprint'),
                               help_text=_("Display at the bottom of the registration form."))

    registered = models.TextField(blank=True,
                                  verbose_name=_("Text after registration"),
                                  help_text=_("Displayed after registration."))

    email = models.EmailField(default='party@fs.tum.de',
                              verbose_name=_("E-Mail"),
                              help_text=_("Used as sender of e-mails."))

    active = models.BooleanField(default=False,
                                 verbose_name=_("Registration possible"))

    admins = models.ManyToManyField(User, blank=True)

    ask_shirt = models.BooleanField(default=True,
                                    verbose_name=_("Ask for T-shirt size"))

    ask_vegetarian = models.BooleanField(default=True,
                                         verbose_name=_("Ask, if helper is vegetarian"))
    show_public_numbers = models.BooleanField(default=True,
                                              verbose_name=_("Show number of helpers on registration page"))

    def __str__(self):
        return self.name

    def is_admin(self, user):
        return user.is_superuser or self.admins.filter(pk=user.pk).exists()

class Job(models.Model):
    """ A job that contains min. 1 shift.

    Columns:
        event: event of this job
        name: name of the job, e.g, Bierstand
        description: longer description of the job
    """
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=200)
    infection_instruction = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.event)

    def shifts_by_day(self):
        tmp_shifts = dict()

        # iterate over all shifts and group them by day
        # (itertools.groupby is strange...)
        for shift in self.shift_set.all():
            day = shift.begin.date()

            # add to list
            if day in tmp_shifts:
                tmp_shifts[day].append(shift)
            # or create begin list
            else:
                tmp_shifts[day] = [shift, ]

        # sort days
        ordered_shifts = OrderedDict(sorted(tmp_shifts.items(),
                                     key=lambda t: t[0]))

        # sort shifts
        for day in ordered_shifts:
            ordered_shifts[day] = sorted(ordered_shifts[day],
                                         key=lambda s : s.begin)

        return ordered_shifts


class Shift(models.Model):
    """ A shift of one job.

    Columns:
        job: job of this shift
        begin: begin of the shift
        end: end of the shift
        number: number of people
    """
    job = models.ForeignKey(Job)
    begin = models.DateTimeField()
    end = models.DateTimeField()
    number = models.IntegerField(default=0)

    def __str__(self):
        return "%s %s (%s)" % (self.job.name, date_filter(self.begin, 'D, d.m H:i'), self.job.event)

    def time(self):
        return "%s - %s" % (date_filter(localtime(self.begin), 'D, d.m, H:i'),
                            date_filter(localtime(self.end), 'H:i'))

    def time_hours(self):
        return "%s - %s" % (date_filter(localtime(self.begin), 'H:i'),
                            date_filter(localtime(self.end), 'H:i'))

    def num_helpers(self):
        return self.helper_set.count()

    def is_full(self):
        return self.num_helpers() >= self.number

    def helpers_percent(self):
        return int(round(self.num_helpers() / self.number * 100, 0))

class Helper(models.Model):
    """ Helper in one or more shifts.

    Columns:
        shifts: all shifts of this person
        prename
        surname
        email
        phone
        comment
        shirt (possible sizes are defined here)
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

    INSTRUCTION_NO= "No"
    INSTRUCTION_YES = "Yes"
    INSTRUCTION_REFRESH = "Refresh"

    INSTRUCTION_CHOICES = (
        (INSTRUCTION_NO, _("I never got an instruction")),
        (INSTRUCTION_YES, _("I have a valid instruction")),
        (INSTRUCTION_REFRESH, _("I got a instruction by a doctor, it must be refreshed"))
    )

    INSTRUCTION_CHOICES_SHORT = (
        (INSTRUCTION_NO, _("No")),
        (INSTRUCTION_YES, _("Valid")),
        (INSTRUCTION_REFRESH, _("Refreshment"))
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    shifts = models.ManyToManyField(Shift)

    prename = models.CharField(max_length=200, verbose_name=_("Prename"))

    surname = models.CharField(max_length=200, verbose_name=_("Surname"))

    email = models.EmailField(verbose_name=_("E-Mail"))

    phone = models.CharField(max_length=200, verbose_name=_("Mobile phone"))

    comment = models.CharField(max_length=200, blank=True,
                               verbose_name=_("Comment"))

    shirt = models.CharField(max_length=20, choices=SHIRT_CHOICES,
                             default=SHIRT_S, verbose_name=_("T-shirt"))

    vegetarian = models.BooleanField(default=False,
                                     verbose_name=_("Vegetarian"),
                                     help_text=_("This helps us to estimate the food for our helpers"))

    infection_instruction = models.CharField(max_length=20,
                                             choices=INSTRUCTION_CHOICES,
                                             blank=True,
                                             verbose_name=_("Instruction for the handling of food"))

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.prename, self.surname)

    def get_infection_instruction_short(self):
        for item in Helper.INSTRUCTION_CHOICES_SHORT:
            if item[0] == self.infection_instruction:
                return item[1]
        return ""

    def send_mail(self):
        if self.shifts.count() == 0:
            return

        event = self.shifts.all()[0].job.event

        subject_template = get_template('registration/mail_subject.txt')
        subject = subject_template.render({ 'event': event }).rstrip()

        text_template = get_template('registration/mail.txt')
        text = text_template.render({ 'user': self })

        send_mail(subject, text, event.email, [self.email],
                  fail_silently=False)
