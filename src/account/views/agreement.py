from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

import datetime

from registration.views.utils import nopermission

from ..models import Agreement, UserAgreement
from ..forms import AgreementForm, UserAgreementForm, DeleteForm

import logging
logger = logging.getLogger("helfertool")


@login_required
def check_user_agreement(request):
    today = datetime.datetime.today().date()

    agreements = Agreement.objects.filter(
        Q(start__lte=today) & (Q(end=None) | Q(end__gte=today)),
    )

    for agreement in agreements:
        user_agreement, created = UserAgreement.objects.get_or_create(
            user=request.user,
            agreement=agreement,
        )

        if not user_agreement.agreed:
            return redirect('account:handle_user_agreement', agreement.pk)

    return redirect('index')


@login_required
def handle_user_agreement(request, agreement_pk):
    agreement = get_object_or_404(Agreement, pk=agreement_pk)

    user_agreement, created = UserAgreement.objects.get_or_create(
        user=request.user,
        agreement=agreement,
    )

    # already agreed -> back to check page
    if user_agreement.agreed or not agreement.in_timeframe:
        return redirect('account:check_user_agreement')

    # ask for agreement
    form = UserAgreementForm(request.POST or None, instance=user_agreement)

    if form.is_valid():
        form.instance.agreed = datetime.datetime.now()
        form.save()

        logger.info("useragreement accepted", extra={
            'user': request.user,
            'agreement': agreement.name,
            'agreement_pk': agreement.pk,
        })

        return redirect('account:check_user_agreement')

    context = {'form': form}
    return render(request, 'account/handle_user_agreement.html', context)


@login_required
def list_agreements(request):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    agreements = Agreement.objects.all()

    context = {'agreements': agreements}
    return render(request, 'account/list_agreements.html',
                  context)


@login_required
def edit_agreement(request, agreement_pk=None):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # get job, if available
    agreement = None
    if agreement_pk:
        agreement = get_object_or_404(Agreement, pk=agreement_pk)

    # form
    form = AgreementForm(request.POST or None, instance=agreement)

    if form.is_valid():
        form.save()

        if agreement:
            logmsg = "useragreement changed"
        else:
            logmsg = "useragreement created"
            agreement = form.instance

        logger.info(logmsg, extra={
            'user': request.user,
            'agreement': agreement.name,
            'agreement_pk': agreement.pk,
        })

        return redirect("account:list_agreements")

    # render page
    context = {"form": form,
               "agreement": agreement}
    return render(request, 'account/edit_agreement.html', context)


@login_required
def delete_agreement(request, agreement_pk):
    # must be superuser
    if not request.user.is_superuser:
        return nopermission(request)

    # form
    form = DeleteForm(request.POST or None)
    agreement = get_object_or_404(Agreement, pk=agreement_pk)

    if form.is_valid():
        logger.info("useragreement deleted", extra={
            'user': request.user,
            'agreement': agreement.name,
            'agreement_pk': agreement.pk,
        })

        agreement.delete()

        return redirect("account:list_agreements")

    # render page
    context = {"form": form,
               "agreement": agreement}
    return render(request, 'account/delete_agreement.html', context)
