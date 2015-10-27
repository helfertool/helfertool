from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMessage

from smtplib import SMTPException

from ..models import Helper


class MailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # get parameters
        self.event = kwargs.pop('event')
        self.user = kwargs.pop('user')
        self.jobs = {}

        super(MailForm, self).__init__(*args, **kwargs)

        # get all allowed jobs
        job_choices = [("", "---------")]

        # admins can send mails to all helpers
        if self.event.is_admin(self.user):
            job_choices.append(("all", _("All helpers")))

        for job in self.event.job_set.all():
            if job.is_admin(self.user):
                job_choices.append(("job_%d" % job.pk, str(job)))
                self.jobs["job_%d" % job.pk] = job

        # sender
        senders = []

        if self.event.is_admin(self.user):
            senders.append((self.event.email, self.event.email))

        senders.append((self.user.email, self.user.email))

        # fields
        self.fields['receiver'] = forms.ChoiceField(
            choices=job_choices,
            label=_("Receivers"),
        )

        self.fields['sender'] = forms.ChoiceField(
            choices=senders,
            label=_("Sender"),
        )

        self.fields['cc'] = forms.EmailField(
            label=_("CC"),
            required=False,
        )

        self.fields['reply-to'] = forms.EmailField(
            label=_("Reply to"),
            required=False,
        )

        self.fields['subject'] = forms.CharField(
            label=_("Subject"),
            max_length=200,
        )

        self.fields['text'] = forms.CharField(
            widget=forms.Textarea,
            label=_("Text"),
        )

    def send_mail(self):
        subject = self.cleaned_data['subject']
        text = self.cleaned_data['text']
        receiver_list = [h.email for h in self._get_helpers()]
        sender = self.cleaned_data['sender']

        # reply to and CC
        reply_to = []
        if self.cleaned_data['reply-to']:
            reply_to = [self.cleaned_data['reply-to'], ]

        cc = []
        if self.cleaned_data['cc']:
            cc = [self.cleaned_data['cc'], ]

        mail = EmailMessage(subject,
                            text,
                            sender,      # from
                            [sender, ],  # to
                            receiver_list,
                            reply_to=reply_to,
                            cc=cc)

        try:
            mail.send(fail_silently=False)
        except (SMTPException, ConnectionError):
            raise

    def _get_helpers(self):
        receiver = self.cleaned_data['receiver']
        if receiver == "all":
            return self.event.helper_set.distinct()
        else:
            return self.jobs[receiver].helpers_and_coordinators()
