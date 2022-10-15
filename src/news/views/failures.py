from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from helfertool.utils import nopermission

from ..forms import FailuresForm

import logging

logger = logging.getLogger("helfertool.news")


@login_required
@never_cache
def failures(request):
    # check if feature is available
    if not settings.FEATURES_NEWSLETTER:
        raise Http404

    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    form = FailuresForm(request.POST or None, user=request.user)

    if form.is_valid():
        form.save()

        messages.success(request, _("Newsletter recipients were updated"))

        return redirect("news:failures")

    context = {
        "form": form,
    }
    return render(request, "news/failures.html", context)
