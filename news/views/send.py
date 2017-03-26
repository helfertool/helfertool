from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

# TODO: move has_sendnews_group somewhere else
from registration.templatetags.permissions import has_sendnews_group
from registration.views.utils import nopermission

from ..models import Person
from ..forms import MailForm


@login_required
def send(request):
    # check permission
    if not (request.user.is_superuser or has_sendnews_group(request.user)):
        return nopermission(request)

    base_url = request.build_absolute_uri(reverse('index'))
    unsubscribe_url = request.build_absolute_uri(reverse('news:unsubscribe',
                                                 args=[settings.FROM_MAIL]))

    form = MailForm(request.POST or None, request=request)
    if form.is_valid():
        form.send_mail()
        messages.success(request, _("Mail are being sent now."))

        return HttpResponseRedirect(reverse('news:send'))

    num_recipients = Person.objects.count()

    context = {'num_recipients': num_recipients,
               'url': base_url,
               'unsubscribe_url': unsubscribe_url,
               'form': form}
    return render(request, 'news/send.html', context)
