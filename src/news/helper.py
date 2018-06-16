from .models import Person


def news_add_email(email):
    obj, created = Person.objects.get_or_create(email=email)


def news_test_email(email):
    try:
        return Person.objects.get(email=email)
    except Person.DoesNotExist:
        return None
