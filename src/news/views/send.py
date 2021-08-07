from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from account.templatetags.globalpermissions import has_sendnews_group
from helfertool.utils import nopermission

from ..forms import MailForm
from ..models import Person

import logging
logger = logging.getLogger("helfertool.news")


@login_required
def send(request):
    # check if feature is available
    if not settings.FEATURES_NEWSLETTER:
        raise Http404

    # check permission
    if not (request.user.is_superuser or has_sendnews_group(request.user)):
        return nopermission(request)

    base_url = request.build_absolute_uri(reverse('index'))
    unsubscribe_url = request.build_absolute_uri(
        reverse('news:unsubscribe',
                args=["1773a8dc-3cf4-497e-9a1c-25128cba768a"]))

    form = MailForm(request.POST or None, request=request)
    if form.is_valid():
        form.send_mail()
        messages.success(request, _("Mails are being sent now."))

        logger.info("newsletter sent", extra={
            'user': request.user,
            'subject': form.cleaned_data['subject'],
        })

        return redirect('news:send')

    num_recipients = Person.objects.filter(validated=True).count()

    context = {'num_recipients': num_recipients,
               'url': base_url,
               'unsubscribe_url': unsubscribe_url,
               'form': form}
    return render(request, 'news/send.html', context)
