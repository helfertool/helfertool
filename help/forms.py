from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _

from .models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = ['sender', 'date', 'done_by']

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('user')

        super(IssueForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.sender = self.sender

        super(IssueForm, self).save(commit)

        mail = EmailMessage("{}: {}".format(
                                _("New issue"),
                                self.instance.get_subject_display()),
                            self.instance.text,
                            settings.CONTACT_MAIL,      # from
                            [settings.CONTACT_MAIL, ],  # to
                            reply_to=[self.sender.email, ])
        mail.send(fail_silently=False)
