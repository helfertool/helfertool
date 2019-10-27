from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import logging
logger = logging.getLogger("helfertool")

from ..models import Person
from ..forms import UnsubscribeForm


def unsubscribe(request, token):
    if not token:
        raise Http404()

    try:
        person = Person.objects.get(token=token)
    except Person.DoesNotExist:
        return render(request, 'news/unsubscribe.html')
    except ValidationError:
        raise Http404()

    form = UnsubscribeForm(request.POST or None)
    if form.is_valid():
        logger.info("newsletter unsubscribe", extra={
            'email': person.email,
        })

        person.delete()

        return HttpResponseRedirect(reverse('news:unsubscribe_done'))

    context = {'person': person}
    return render(request, 'news/unsubscribe.html', context)
