from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext as _

import logging
logger = logging.getLogger("helfertool")

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
