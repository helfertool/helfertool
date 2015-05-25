from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.template import Context
from django.template.defaultfilters import date as date_filter
from django.template.loader import get_template
from django.utils.timezone import localtime
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
                                validators=[RegexValidator('^[a-zA-Z0-9]+$')])
    name = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    imprint = models.TextField(blank=True)
    registered = models.TextField(blank=True)
    email = models.EmailField(default='party@fs.tum.de')
    active = models.BooleanField(default=False)
    ask_shirt = models.BooleanField(default=True)
    ask_vegetarian = models.BooleanField(default=True)
    admins = models.ManyToManyField(User, blank=True)

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

    def is_full(self):
        return self.helper_set.count() >= self.number


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
        (INSTRUCTION_NO, 'Einweisung noch nie erhalten'),
        (INSTRUCTION_YES, 'Einweisung gültig'),
        (INSTRUCTION_REFRESH, 'Ersteinweisung durch Arzt erhalten, Auffrischung nötig')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    shifts = models.ManyToManyField(Shift)
    prename = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=200)
    comment = models.CharField(max_length=200, blank=True)
    shirt = models.CharField(max_length=20, choices=SHIRT_CHOICES,
                             default=SHIRT_S)
    vegetarian = models.BooleanField(default=False)
    infection_instruction = models.CharField(max_length=20,
                                             choices=INSTRUCTION_CHOICES,
                                             blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.prename, self.surname)

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
