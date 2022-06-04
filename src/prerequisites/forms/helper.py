from django import forms

from ..utils import prerequisites_for_helper

import logging

logger = logging.getLogger("helfertool.prerequisites")


class HelperPrerequisiteForm(forms.Form):
    """
    Shows all needed prerequisites for a helper
    """

    def __init__(self, *args, **kwargs):
        self._helper = kwargs.pop("helper")
        self._user = kwargs.pop("user")

        super(HelperPrerequisiteForm, self).__init__(*args, **kwargs)

        # create fields and store the prerequisites for later use
        self._prerequisites = {}
        for prereqisite in prerequisites_for_helper(self._helper):
            id_str = "prerequisite_{}".format(prereqisite.pk)

            self._prerequisites[id_str] = prereqisite

            self.fields[id_str] = forms.BooleanField(
                label=prereqisite.name, required=False, initial=prereqisite.check_helper(self._helper)
            )

    def save(self):
        if self._prerequisites and self.has_changed():
            for id_str, prerequisite in self._prerequisites.items():
                state = self.cleaned_data[id_str]
                prerequisite.set_helper(self._helper, state)

                # logging per prerequisite (if changed)
                if id_str in self.changed_data:
                    logger.info(
                        "helper prerequisites",
                        extra={
                            "user": self._user,
                            "event": self._helper.event,
                            "helper": self._helper,
                            "prerequisite": prerequisite.name,
                            "prerequisite_pk": prerequisite.pk,
                            "state": state,
                        },
                    )

    def has_items(self):
        return bool(self.fields)

    def has_unfilfilled(self):
        for prerequisite in self._prerequisites.values():
            if not prerequisite.check_helper(self._helper):
                return True
        return False
