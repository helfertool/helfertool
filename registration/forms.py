from django import forms

from .models import Helper

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = ['prename', 'surname', 'email', 'phone', 'shirt', 'comment']

    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('event')
        super(RegisterForm, self).__init__(*args, **kwargs)
#
#        for i, question in enumerate(extra):
#            self.fields['custom_%s' % i] = forms.CharField(label=question)
