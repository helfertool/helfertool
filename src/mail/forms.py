from django import forms
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import gettext_lazy as _

from django_select2.forms import Select2MultipleWidget
from smtplib import SMTPException

from .models import SentMail, MailDelivery
from .tracking import new_tracking_event

from registration.permissions import has_access, ACCESS_MAILS_SEND


class MailFormError(Exception):
    """Error during mail sending. The message will be displayed to the user, so do not include sensitive data."""

    pass


class MailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # get parameters
        self.event = kwargs.pop("event")
        self.user = kwargs.pop("user")

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

        # check if we can send mails to all helpers
        if has_access(self.user, self.event, ACCESS_MAILS_SEND):
            tmp = []
            tmp.append(("all", _("All helpers and coordinators")))
            tmp.append(("all-coords", _("All coordinators")))

            choices.append((_("General"), tmp))

        for job in self.event.job_set.all():
            if has_access(self.user, job, ACCESS_MAILS_SEND):
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

        # reply to
        reply_to = []

        if has_access(self.user, self.event, ACCESS_MAILS_SEND):
            reply_to.append((self.event.email, self.event.email))

        reply_to.append((self.user.email, self.user.email))
        reply_to.append(("-", _("Custom")))

        # fields
        self.fields["receiver"] = forms.MultipleChoiceField(
            choices=choices,
            label=_("Receivers"),
            widget=Select2MultipleWidget,
        )

        self.fields["reply_to"] = forms.ChoiceField(
            choices=reply_to,
            label=_("Reply to"),
        )
        self.fields["reply_to"].widget.attrs["onChange"] = "handle_reply_to()"

        self.fields["custom_reply_to"] = forms.EmailField(
            label=_("Custom reply to"),
            help_text=_('Only used if "Custom" is selected above.'),
            required=False,
        )

        self.fields["cc"] = forms.EmailField(
            label=_("CC"),
            required=False,
        )

        self.fields["subject"] = forms.CharField(
            label=_("Subject"),
            max_length=200,
        )

        self.fields["text"] = forms.CharField(
            widget=forms.Textarea,
            label=_("Text"),
        )

    def clean(self):
        cleaned_data = super(MailForm, self).clean()

        if cleaned_data.get("reply_to") == "-" and not cleaned_data.get("custom_reply_to"):
            raise forms.ValidationError(_("You must specify a custom reply to address."))

        # check if there are recipients (will be checked again in send_mail, but we can provide better feedback here)
        if not self._get_helpers():
            raise forms.ValidationError(_("There are no helpers or coordinators that would receive this mail."))

    def send_mail(self):
        # basic parameters
        subject = self.cleaned_data.get("subject")
        text = self.cleaned_data.get("text")

        reply_to = self.cleaned_data.get("reply_to")
        if reply_to == "-":
            reply_to = self.cleaned_data.get("custom_reply_to")

        # model for log
        sentmail = SentMail.objects.create(
            event=self.event,
            user=self.user,
            sender=settings.EMAIL_SENDER_ADDRESS,
            subject=subject,
            text=text,
            reply_to=reply_to,
        )

        # CC
        cc = []
        if self.cleaned_data.get("cc"):
            cc = [
                self.cleaned_data.get("cc"),
            ]
            sentmail.cc = self.cleaned_data.get("cc")

        # tracking id
        tracking_uuid, tracking_header = new_tracking_event()
        sentmail.tracking_uuid = tracking_uuid

        # get the helpers that should receive the mail
        helpers = self._get_helpers(sentmail)

        # create mail delivery entry for tracking and a unique list of mail addresses
        receiver_list = []
        for h in helpers:
            MailDelivery.objects.create(helper=h, sentmail=sentmail)

            if h.email not in receiver_list:
                receiver_list.append(h.email)

        # save changed cc, tracking_uuid and things done in _get_helpers
        sentmail.save()

        if not receiver_list:
            sentmail.failed = True
            sentmail.save()
            raise MailFormError(_("There are no helpers or coordinators that would receive this mail."))

        # send mail now
        mail = EmailMessage(
            subject,
            text,
            settings.EMAIL_SENDER_ADDRESS,
            [
                reply_to,
            ],  # to
            receiver_list,
            reply_to=[
                reply_to,
            ],
            cc=cc,
            headers=tracking_header,
        )

        try:
            mail.send(fail_silently=False)
        except (SMTPException, ConnectionError):
            sentmail.failed = True
            sentmail.save()
            raise

    def _get_helpers(self, sentmail=None):
        """Get the helpers that would receive the mail.

        If `sentmail` if provided the `SentMail` object is updated to contain this info."""
        receiver_list = self.cleaned_data.get("receiver")

        tmp = []

        for receiver in receiver_list:
            # all helpers and coordinators - special case: we can abort now
            if receiver == "all":
                if sentmail:
                    sentmail.all_helpers_and_coordinators = True
                return self.event.helper_set.distinct()
            # all coordinators
            elif receiver == "all-coords":
                tmp.extend(self.event.all_coordinators)
                if sentmail:
                    sentmail.all_coordinators = True
            # helpers and coordinators for job
            elif receiver in self.jobs_all:
                job_obj = self.jobs_all[receiver]
                tmp.extend(job_obj.helpers_and_coordinators())
                if sentmail:
                    sentmail.jobs_all.add(job_obj)
            # only coordinators for job
            elif receiver in self.jobs_coordinators:
                job_obj = self.jobs_coordinators[receiver]
                tmp.extend(job_obj.coordinators.all())
                if sentmail:
                    sentmail.jobs_only_coordinators.add(job_obj)
            # single shifts
            elif receiver in self.shifts:
                shift_obj = self.shifts[receiver]
                tmp.extend(shift_obj.helper_set.all())
                if sentmail:
                    sentmail.shifts.add(shift_obj)

        return tmp
