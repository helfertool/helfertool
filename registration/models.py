from django.db import models


class Event(models.Model):
    """ Event for registration.

    Columns:
        name: the name of the event
        text: text at begin of registration
        imprint: text at the end of registration
        active: is the registration opened?
    """
    name = models.CharField(max_length=200)
    text = models.TextField()
    imprint = models.TextField()
    active = models.BooleanField(default=False)


class Job(models.Model):
    """ A job that contains min. 1 shift.

    Columns:
        event: event of this job
        name: name of the job, e.g, Bierstand
        description: longer description of the job
    """
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=200)
    description = models.TextField()


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

    shifts = models.ManyToManyField(Shift)
    prename = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=200)
    comment = models.TextField()
    shirt = models.CharField(max_length=20, choices=SHIRT_CHOICES,
                             default=SHIRT_S)
