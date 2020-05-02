from django import forms
from ..models import Prerequisite

import logging
logger = logging.getLogger("helfertool")

class RegistrationPrerequisiteForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.registerform = kwargs.pop('registerform')

        super(RegistrationPrerequisiteForm, self).__init__(*args, **kwargs)

        # create fields and store the prerequisites for later use
        for prerequisite in Prerequisite.objects.filter(event=self.event).distinct():
            id_str = str(prerequisite.name)



            self.fields[id_str] = forms.BooleanField(
                label=prerequisite.name,
                required=False
            )

    def save(self, request):
        logger.info("registration prerequisites", extra={
            'user': request.user,
            'event': self.helper.event,
        })

    def has_items(self):
        return bool(self.fields)