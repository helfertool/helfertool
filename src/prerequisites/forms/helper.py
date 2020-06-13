from django import forms

from ..utils import prerequisites_for_helper

import logging
logger = logging.getLogger("helfertool.prerequisites")


class HelperPrerequisiteForm(forms.Form):
    """
    Shows all needed prerequisites for a helper
    """

    def __init__(self, *args, **kwargs):
        self.helper = kwargs.pop('helper')

        super(HelperPrerequisiteForm, self).__init__(*args, **kwargs)

        # create fields and store the prerequisites for later use
        self._prerequisites = {}
        for prereqisite in prerequisites_for_helper(self.helper):
            id_str = "prerequisite_{}".format(prereqisite.pk)

            self._prerequisites[id_str] = prereqisite

            self.fields[id_str] = forms.BooleanField(
                label=prereqisite.name,
                required=False,
                initial=prereqisite.check_helper(self.helper)
            )

    def save(self, request):
        if self._prerequisites:
            for id_str, prerequisite in self._prerequisites.items():
                prerequisite.set_helper(self.helper, self.cleaned_data[id_str])

            logger.info("helper prerequisites", extra={
                'user': request.user,
                'event': self.helper.event,
                'helper': self.helper,
            })

    def has_items(self):
        return bool(self.fields)

    def has_unfilfilled(self):
        for prerequisite in self._prerequisites.values():
            if not prerequisite.check_helper(self.helper):
                return True
        return False
