from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from captcha.fields import CaptchaField
from helfertool.forms import CustomCaptchaTextInput

from news.helper import news_add_email

from .widgets import ShiftTableRegistrationWidget
from ..models import Helper, Shift

import itertools


class RegisterForm(forms.ModelForm):
    """Form for registration of helpers.

    This form asks for the personal data and handles the selection of shifts.
    """

    class Meta:
        model = Helper
        fields = [
            "firstname",
            "surname",
            "email",
            "phone",
            "shirt",
            "nutrition",
            "infection_instruction",
            "comment",
            "privacy_statement",
            "shifts",
        ]
        widgets = {
            "shifts": ShiftTableRegistrationWidget,
        }

    def __init__(self, *args, **kwargs):
        """Customize the form.

        Some fields like 'shirt' are removed, if they are not necessary.
        """
        self.event = kwargs.pop("event")
        self.shifts_qs = kwargs.pop("shifts_qs", None)
        self.preselected_shifts = kwargs.pop("preselected_shifts", None)
        self.is_internal = kwargs.pop("is_internal", False)
        self.is_link = kwargs.pop("is_link", False)

        super(RegisterForm, self).__init__(*args, **kwargs)

        # remove field for phone number?
        if not self.event.ask_phone:
            self.fields.pop("phone")

        # remove field for shirt?
        if not self.event.ask_shirt:
            self.fields.pop("shirt")
        else:
            # restrict choices
            self.fields["shirt"].choices = self.event.get_shirt_choices(internal=self.is_internal)

        # remove field for nutrition?
        if not self.event.ask_nutrition:
            self.fields.pop("nutrition")

        # remove field for privacy statement?
        if self.is_internal:
            self.fields.pop("privacy_statement")
        else:
            # add link to show privacy statement after label
            privacy_label = format_html(
                '{} (<a href="" data-bs-toggle="modal" data-bs-target="#privacy">{}</a>)',
                self.fields["privacy_statement"].label,
                _("Show"),
            )
            self.fields["privacy_statement"].label = privacy_label

        # add field for age?
        self.ask_full_age = self.event.ask_full_age and not self.is_internal
        if self.ask_full_age:
            self.fields["full_age"] = forms.BooleanField(label=_("I confirm to be full aged."), required=False)

        # add field for notification about new events?
        self.ask_news = self.event.ask_news and not self.is_internal
        if self.ask_news:
            news_label = format_html(
                '{} (<a href="" data-bs-toggle="modal" data-bs-target="#privacy-newsletter">{}</a>)',
                _("I want to be informed about future events that are looking for helpers."),
                _("Show privacy statement"),
            )
            self.fields["news"] = forms.BooleanField(label=news_label, required=False)

        # add captcha?
        self.ask_captcha = settings.CAPTCHAS_REGISTRATION and not self.is_internal
        if self.ask_captcha:
            self.fields["captcha"] = CaptchaField(widget=CustomCaptchaTextInput)

        # specify, which shifts are included in the form
        if not self.shifts_qs:
            self.shifts_qs = Shift.objects.filter(job__event=self.event, job__public=True, hidden=False)
            self.respect_blocked = True
        else:
            self.respect_blocked = False

        # set preselected shifts to "checked"
        self.fields["shifts"].queryset = self.shifts_qs
        self.fields["shifts"].initial = self.preselected_shifts
        self.fields["shifts"].required = False  # will be checked in clean with a nice error message
        self.fields["shifts"].widget.respect_blocked = self.respect_blocked

    def clean(self):
        """Custom validation of shifts and other fields.

        This method performs some validations:
          * The helper must register for at least one shift.
          * The field 'infection_instruction' must be set, if one of the
            selected shifts requires this.
          * The selected shift is not full.
          * The shifts do not overlap (if configured)
        """
        super(RegisterForm, self).clean()

        # check if event is archived -> block
        if self.event.archived:
            raise ValidationError(_("The registration is not possible as the event is archived."))

        # Public registration is visible for involved users of the event.
        # But it should not work for them if the public registration is not active.
        if not self.is_internal and not self.event.active and not self.is_link:
            raise ValidationError(
                _("The public registration for this event is disabled. " "Use the form in the admin interface.")
            )

        # check if shift was selected
        if not self.cleaned_data.get("shifts"):
            raise ValidationError(_("You must select at least one shift."))

        # check if helper if full age (but continue with further checks)
        if self.ask_full_age and not self.cleaned_data.get("full_age"):
            self.add_error("full_age", _("We are not allowed to accept helpers that are not of full age."))

        # check if the data privacy statement was accepted (but continue with further checks)
        if not self.is_internal and not self.cleaned_data.get("privacy_statement"):
            self.add_error("privacy_statement", _("Please accept the data privacy statement."))

        # iterate over all (selected) shifts
        infection_instruction_needed = False
        for shift in self.cleaned_data.get("shifts"):
            # check if infection instruction is needed for one of the shifts
            if shift.job.infection_instruction:
                infection_instruction_needed = True

            # check if shift is full
            if shift.is_full():
                raise ValidationError(_("You selected a full shift."))

            # check if shift is blocked
            if shift.blocked and self.respect_blocked:
                raise ValidationError(_("You selected a blocked shift."))

        # infection instruction needed but field not set?
        if infection_instruction_needed and not self.cleaned_data.get("infection_instruction"):
            self.add_error(
                "infection_instruction",
                _("Please tell us, if you received already an instruction for the handling of food."),
            )

        # check for overlapping shifts
        if self.event.max_overlapping is not None:
            max_overlap = self.event.max_overlapping
            if self._check_has_overlap(max_overlap):
                raise ValidationError(
                    _("Some of your shifts overlap more then %(minutes)d minutes.") % {"minutes": max_overlap}
                )

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(False)
        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m()

        # add to news
        if self.ask_news and self.cleaned_data.get("news"):
            news_add_email(self.cleaned_data.get("email"), withevent=True)

        return instance

    def _check_has_overlap(self, max_overlap):
        """
        Check if any two shifts from the argument list are overlapping
        The arguments are the keys of the shifts

        :return: true of overlap exists
        """

        for shifts in itertools.combinations(self.cleaned_data.get("shifts"), 2):
            s1 = shifts[0]
            s2 = shifts[1]

            # check if shifts overlap (1st or term) or one shift is part
            # of the other shift (2nd and 3rd or term)
            if (
                (
                    (s2.end - s1.begin).total_seconds() > max_overlap * 60
                    and (s1.end - s2.begin).total_seconds() > max_overlap * 60
                )
                or (s1.begin >= s2.begin and s1.end <= s2.end)
                or (s2.begin >= s1.begin and s2.end <= s1.end)
            ):
                return True
        return False


class DeregisterForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = []

    def __init__(self, *args, **kwargs):
        self.shift = kwargs.pop("shift")

        super(DeregisterForm, self).__init__(*args, **kwargs)

    def delete(self):
        self.instance.shifts.remove(self.shift)
