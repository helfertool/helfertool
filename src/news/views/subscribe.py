from django.conf import settings
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import logging
logger = logging.getLogger("helfertool.news")

from ..forms import SubscribeForm


def subscribe(request):
    # check if feature is available
    if not settings.FEATURES_NEWSLETTER:
        raise Http404

    form = SubscribeForm(request.POST or None)
    if form.is_valid():
        form.save()

        logger.info("newsletter subscribe", extra={
            'email': form.instance.email,
            'withevent': False,
        })

        return HttpResponseRedirect(reverse('news:subscribe_done'))

    context = {'form': form}
    return render(request, 'news/subscribe.html', context)
