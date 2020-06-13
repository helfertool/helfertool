from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import logging
logger = logging.getLogger("helfertool.news")

from ..forms import SubscribeForm


def subscribe(request):
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
