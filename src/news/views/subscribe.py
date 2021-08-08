from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from ..forms import SubscribeForm
from ..helper import news_add_email, news_validate_person
from ..models import Person

import logging
logger = logging.getLogger("helfertool.news")


def subscribe(request):
    # check if feature is available
    if not settings.FEATURES_NEWSLETTER:
        raise Http404

    form = SubscribeForm(request.POST or None)
    if form.is_valid():
        person, created = news_add_email(form.cleaned_data["email"], withevent=False)

        if created:
            person.send_validation_mail(request)

        return redirect('news:subscribe_done')

    context = {'form': form}
    return render(request, 'news/subscribe.html', context)


def subscribe_confirm(request, token):
    # check if feature is available
    if not settings.FEATURES_NEWSLETTER:
        raise Http404

    # check token
    try:
        person = Person.objects.get(token=token)
    except Person.DoesNotExist:
        # token does not exists (anymore) -> show error and redirect to subscribe page
        messages.error(request, _("The link is not valid anymore. Please subscribe again."))
        return redirect('news:subscribe')
    except ValidationError:
        raise Http404()

    if not person.validated:
        news_validate_person(person)

    context = {'person': person}
    return render(request, 'news/subscribe_confirm.html', context)
