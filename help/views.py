from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from smtplib import SMTPException

from .forms import IssueForm


@login_required
def create_issue(request):
    form = IssueForm(request.POST or None, user=request.user)

    if form.is_valid():
        try:
            form.save()
            messages.success(request, _("The issue was saved and sent to the "
                                        "admins."))
        except (SMTPException, ConnectionError) as e:
            messages.error(request, _("The issue was created but notifying "
                                      "the admins failed: %(error)s") %
                           {'error': str(e)})

        return HttpResponseRedirect(reverse('help:create_issue'))

    context = {'form': form}
    return render(request, 'help/create_issue.html', context)
