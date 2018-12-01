from .models import Person

import logging
logger = logging.getLogger("helfertool")


def news_add_email(email):
    obj, created = Person.objects.get_or_create(email=email)

    logger.info("newsletter subscribe", extra={
        'email': obj.email,
        'withevent': True,
    })


def news_test_email(email):
    try:
        return Person.objects.get(email=email)
    except Person.DoesNotExist:
        return None
