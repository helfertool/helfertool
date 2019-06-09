from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from registration.views.utils import nopermission

from ..forms import RemoveForm

import logging
logger = logging.getLogger("helfertool")


@login_required
def remove(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    form = RemoveForm(request.POST or None)
    if form.is_valid():
        email = form.delete()

        messages.success(request, _("Recipient removed."))

        logger.info("newsletter removed", extra={
            'email': email,
        })

        return redirect('news:remove')

    context = {'form': form}
    return render(request, 'news/remove.html', context)
