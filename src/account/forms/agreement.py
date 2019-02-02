from django import forms

import datetime

from ..models import UserAgreement


class UserAgreementForm(forms.ModelForm):
    class Meta:
        model = UserAgreement
        fields = []
