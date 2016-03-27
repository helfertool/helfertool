from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMessage

from smtplib import SMTPException


class MailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # get parameters
        self.event = kwargs.pop('event')
        self.user = kwargs.pop('user')

        # different select values

        # send to helpers and coordinators
        self.jobs_all = {}

        # only coordinators
        self.jobs_coordinators = {}

        # single shifts
        self.shifts = {}

        super(MailForm, self).__init__(*args, **kwargs)

        # get all allowed jobs
        choices = []

        # admins can send mails to all helpers
        if self.event.is_admin(self.user):
            tmp = []
            tmp.append(("all", _("All helpers and coordinators")))
            tmp.append(("all-coords", _("All coordinators")))

            choices.append((_("General"), tmp))

        for job in self.event.job_set.all():
            if job.is_admin(self.user):
                tmp = []

                # helpers and coordinators
                title = _("{}, Helpers and coordinators").format(job.name)
                tmp.append(("job_%d_all" % job.pk, title))
                self.jobs_all["job_%d_all" % job.pk] = job

                # only coordinators
                title = _("{}, Coordinators").format(job.name)
                tmp.append(("job_%d_coords" % job.pk, title))
                self.jobs_coordinators["job_%d_coords" % job.pk] = job

                # shifts
                for shift in job.shift_set.all():
                    tmp.append(("shift_%d" % shift.pk, str(shift)))
                    self.shifts["shift_%d" % shift.pk] = shift

                choices.append((job.name, tmp))

        # sender
        senders = []

        if self.event.is_admin(self.user):
            senders.append((self.event.email, self.event.email))

        senders.append((self.user.email, self.user.email))

        # fields
        self.fields['receiver'] = forms.MultipleChoiceField(
            choices=choices,
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
        sender = self.cleaned_data['sender']

        # get unique list of mail addresses
        seen = set()
        seen_add = seen.add  # performance FTW!
        receiver_list = [h.email for h in self._get_helpers()
                         if not (h.email in seen or seen_add(h.email))]

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
        except SMTPException:
            raise

    def _get_helpers(self):
        receiver_list = self.cleaned_data['receiver']

        tmp = []

        for receiver in receiver_list:
            if receiver == "all":
                return self.event.helper_set.distinct()
            elif receiver == "all-coords":
                tmp.extend(self.event.all_coordinators)
            # helpers and coordinators for job
            elif receiver in self.jobs_all:
                tmp.extend(self.jobs_all[receiver].helpers_and_coordinators())
            # only coordinators for job
            elif receiver in self.jobs_coordinators:
                tmp.extend(self.jobs_coordinators[receiver].coordinators.all())
            # single shifts
            elif receiver in self.shifts:
                tmp.extend(self.shifts[receiver].helper_set.all())

        return tmp
