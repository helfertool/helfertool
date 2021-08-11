from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..forms import RemoveForm

import logging
logger = logging.getLogger("helfertool.news")


@login_required
@never_cache
def remove(request):
    # check if feature is available
    if not settings.FEATURES_NEWSLETTER:
        raise Http404

    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    form = RemoveForm(request.POST or None)
    if form.is_valid():
        email = form.delete()

        messages.success(request, _("Recipient removed."))

        logger.info("newsletter removed", extra={
            'user': request.user,
            'email': email,
        })

        return redirect('news:remove')

    context = {'form': form}
    return render(request, 'news/remove.html', context)
