from django import forms
from django_select2.forms import ModelSelect2Widget

from ..models import Helper


class SingleHelperSelectWidget(ModelSelect2Widget):
    """ Select2 widget for a single helper.
    The search looks at the first and last name. """
    model = Helper

    search_fields = [
        'firstname__icontains',
        'surname__icontains',
    ]

    def label_from_instance(self, obj):
        return obj.full_name


class ShiftTableWidget(forms.CheckboxSelectMultiple):
    """ Widget for ManyToMany fields to Shift objects.
    Most of the things happen in the templatetag form_shifttable and are documented there.

    The widget only defines the templates.

    The field must be rendered with the templatetag form_shifttable."""
    template_name = "registration/templatetags/form_shifttable_standard.html"
    option_template_name = "registration/templatetags/form_shifttable_option_standard.html"


class ShiftTableRegistrationWidget(forms.CheckboxSelectMultiple):
    """ Same as ShiftTableWidget, but with specific templates for registration form."""
    template_name = "registration/templatetags/form_shifttable_registration.html"
    option_template_name = "registration/templatetags/form_shifttable_option_registration.html"

    # disable blocked shifts?
    respect_blocked = True

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)

        # transfer respect_blocked to context, so that we can use it in templatetag
        # form_shifttable_shift_registration
        context["widget"]["respect_blocked"] = self.respect_blocked

        return context
