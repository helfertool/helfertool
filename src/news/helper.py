from .models import Person

import logging
logger = logging.getLogger("helfertool.news")


def news_add_email(email, withevent=True):
    """ Subscribe email address to newsletter.
    The confirmation mail is not sent by this function.

    Returns the `Person` object and `created` flag.
    """
    person, created = Person.objects.get_or_create(
        email=email,
        defaults={"withevent": withevent},
    )

    if created:
        # only log, if explicitly subscribed or really created
        logger.info("newsletter subscribe", extra={
            'email': person.email,
            'withevent': withevent,
        })

    return person, created
