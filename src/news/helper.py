from django.utils import timezone

from .models import Person

import logging
logger = logging.getLogger("helfertool.news")


def news_add_email(email, withevent=False):
    """ Subscribe email address to newsletter.
    The confirmation mail is not sent by this function.

    Returns the `Person` object and `created` flag.
    """
    person, created = Person.objects.get_or_create(
        email=email,
        defaults={
            "withevent": withevent,
        },
    )

    if created:
        # only log, if explicitly subscribed or really created
        logger.info("newsletter subscribe", extra={
            'email': person.email,
            'withevent': withevent,
        })

    return person, created


def news_validate_person(person):
    """ Validate a person. """
    person.validated = True
    person.timestamp_validated = timezone.now()
    person.save()

    logger.info("newsletter validated", extra={
        'email': person.email,
    })


def news_validate_helper(helper):
    """ Validate a person, but based on the helper object.
    The matching person objects are identified based on the mail address.
    """
    persons = Person.objects.filter(email=helper.email, validated=False)
    for p in persons:
        news_validate_person(p)
