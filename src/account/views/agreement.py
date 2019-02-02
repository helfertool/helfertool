from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

import datetime

from ..models import Agreement, UserAgreement
from ..forms import UserAgreementForm


@login_required
def check_user_agreement(request):
    agreements = Agreement.objects.filter(begin__gte=datetime.datetime.today())

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
    if user_agreement.agreed:
        return redirect('account:check_user_agreement')

    # ask for agreement
    form = UserAgreementForm(request.POST or None, instance=user_agreement)

    if form.is_valid():
        form.instance.agreed = datetime.datetime.now()
        form.save()
        return redirect('account:check_user_agreement')

    context = {'form': form}
    return render(request, 'account/handle_user_agreement.html', context)
