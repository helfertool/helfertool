from .models import Person

def news_add_email(email):
    obj, created = Person.objects.get_or_create(email=email)
