from django.conf import settings
from django.urls import reverse

from django_ical.views import ICalFeed

from registration.utils import get_or_404


class HelperFeed(ICalFeed):
    timezone = settings.TIME_ZONE
    product_id = "-//helfertool.org//Helfertool"

    def get_object(self, request, event_url_name, helper_pk):
        event, job, shift, helper = get_or_404(event_url_name, helper_pk=helper_pk)
        self._event = event
        self._helper = helper
        self._registered_link = reverse('registered', args=[event.url_name, helper.pk])

        return helper

    def file_name(self, helper):
        return "{}.ics".format(helper.event.name)

    def items(self, helper):
        return helper.shifts.all()

    def item_title(self, shift):
        return "{} - {}".format(self._event.name, shift.job.name)

    def item_description(self, shift):
        return ""

    def item_link(self, shift):
        return self._registered_link

    def item_start_datetime(self, shift):
        return shift.begin

    def item_end_datetime(self, shift):
        return shift.end

    def item_guid(self, shift):
        return "{}#{}".format(self.item_link(shift), shift.pk)
