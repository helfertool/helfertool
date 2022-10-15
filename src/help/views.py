from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from .forms import IssueForm

from smtplib import SMTPException


@login_required
@never_cache
def create_issue(request):
    form = IssueForm(request.POST or None, user=request.user)

    if form.is_valid():
        try:
            form.save()
            messages.success(request, _("The issue was saved and sent to the admins."))
        except (SMTPException, ConnectionError):
            messages.error(request, _("The issue was created but notifying the admins failed"))

        return redirect("help:create_issue")

    context = {"form": form}
    return render(request, "help/create_issue.html", context)
