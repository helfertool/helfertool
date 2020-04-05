from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

import logging
logger = logging.getLogger("helfertool")

from account.templatetags.globalpermissions import has_sendnews_group
from registration.views.utils import nopermission

from ..models import Person
from ..forms import MailForm


@login_required
def send(request):
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

        return HttpResponseRedirect(reverse('news:send'))

    num_recipients = Person.objects.count()

    context = {'num_recipients': num_recipients,
               'url': base_url,
               'unsubscribe_url': unsubscribe_url,
               'form': form}
    return render(request, 'news/send.html', context)
