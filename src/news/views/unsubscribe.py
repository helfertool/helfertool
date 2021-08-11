from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

from ..forms import UnsubscribeForm
from ..models import Person

import logging
logger = logging.getLogger("helfertool.news")


@never_cache
def unsubscribe(request, token):
    # check if feature is available and token is there
    if not settings.FEATURES_NEWSLETTER or not token:
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

        return redirect('news:unsubscribe_done')

    context = {'person': person}
    return render(request, 'news/unsubscribe.html', context)
