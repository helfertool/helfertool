from django import forms
from django.utils.translation import ugettext as _

from pretix.models import PretixItemJobLinkage
from pretix.pretix_client import enumerate_items


class PretixSettingsForm(forms.Form):
    def __init__(self, event, data, *args, **kwargs):
        super(PretixSettingsForm, self).__init__(data=data, *args, **kwargs)
        self.event = event
        self.jobs = self.event.job_set.all()
        self.pretix_items, pretix_errors = enumerate_items(event)

        # xxx cleaned_data has to be set if we want to add an error
        if not hasattr(self, "cleaned_data"):
            self.cleaned_data = {}

        self.warnings = []
        for prefix_error in pretix_errors:
            self.warnings.append(f"Could not retrieve {prefix_error} from pretix")

        items = [(None, "-")]

        for item in self.pretix_items:
            items.append((item.ref, f"{item.org_name} - {item.event_name} - {item.item_name}"))

        for job in self.jobs:
            field_name = "job_%d_item" % job.pk

            item_gone = False
            try:
                initial_item_ref = PretixItemJobLinkage.objects.get(job=job).pretix_item_ref
                if not any((initial_item_ref == item.ref for item in self.pretix_items)):
                    initial_item_ref = None
                    item_gone = True
            except PretixItemJobLinkage.DoesNotExist:
                initial_item_ref = None

            new_item_ref = self.data.get(field_name)
            if new_item_ref is not None:
                if new_item_ref == "":
                    item_gone = False
                elif any((new_item_ref == item.ref for item in self.pretix_items)):
                    item_gone = False
                else:
                    item_gone = True

            self.fields[field_name] = forms.ChoiceField(
                choices=items,
                required=False,
                initial=initial_item_ref,
                label=_("Pretix ticket type"),
            )
            if item_gone:
                self.add_error(field_name, _("Could not find in Pretix"))

    def save(self):
        for job in self.jobs:
            item_ref = self.cleaned_data["job_%d_item" % job.pk]
            if item_ref:
                PretixItemJobLinkage.objects.update_or_create(job=job, defaults={"pretix_item_ref": item_ref})
            else:
                PretixItemJobLinkage.objects.filter(job=job).delete()
