from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Count
from django.utils.translation import ugettext as _
from django.urls import reverse

from badges.models import SpecialBadges
from helfertool.forms import DatePicker, SingleUserSelectWidget, ImageFileInput
from toollog.models import LogEntry

from ..models import Event, EventAdminRoles, EventArchive

from ckeditor.widgets import CKEditorWidget
from copy import deepcopy

import os


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['admins', 'text', 'imprint', 'registered', 'badge_settings', 'archived', ]
        widgets = {
            'text': CKEditorWidget,
            'date': DatePicker,
            'changes_until': DatePicker,
            'logo': ImageFileInput,
            'logo_social': ImageFileInput,
        }

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for w in ('text', 'imprint', 'registered'):
            for lang, name in settings.LANGUAGES:
                widgets["{}_{}".format(w, lang)] = CKEditorWidget()

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        # disable most fields if event is archived
        if self.instance.archived:
            for field_id in self.fields:
                if field_id != "url_name":
                    self.fields[field_id].disabled = True

        if not self.instance.ask_shirt and 'shirt_sizes' in self.fields:
            # 'shirt_sizes' is not in fields for EventDuplicateForm
            self.fields.pop('shirt_sizes')

        # remove flags for disabled features
        if not settings.FEATURES_NEWSLETTER and 'ask_news' in self.fields:
            self.fields.pop('ask_news')
        if not settings.FEATURES_BADGES and 'badges' in self.fields:
            self.fields.pop('badges')
        if not settings.FEATURES_GIFTS and 'gifts' in self.fields:
            self.fields.pop('gifts')
        if not settings.FEATURES_PREREQUISITES and 'prerequisites' in self.fields:
            self.fields.pop('prerequisites')
        if not settings.FEATURES_INVENTORY and 'inventory' in self.fields:
            self.fields.pop('inventory')
        if not settings.FEATURES_CORONA and 'corona' in self.fields:
            self.fields.pop('corona')

        # change labels of ckeditor fields: We only want to have the language name as label
        # everything else is in the template.
        for field in ('text', 'imprint', 'registered'):
            for lang, name in settings.LANGUAGES:
                field_name = "{}_{}".format(field, lang)
                if field_name in self.fields:
                    self.fields[field_name].label = name

        # set download_url parameters for widgets
        # EventDuplicateForm inherits from EventForm, but does not have a logo field, so check this here
        if self.instance.pk and "logo" in self.fields:
            url_name = self.instance.url_name
            self.fields["logo"].widget.download_url = reverse("get_event_logo", args=[url_name, "default"])
            self.fields["logo_social"].widget.download_url = reverse("get_event_logo", args=[url_name, "social"])


class EventAdminRolesForm(forms.ModelForm):
    class Meta:
        model = EventAdminRoles
        fields = ['roles', ]


class EventAdminRolesAddForm(forms.ModelForm):
    class Meta:
        model = EventAdminRoles
        fields = ['user', 'roles', ]
        widgets = {
            'user': SingleUserSelectWidget,
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(EventAdminRolesAddForm, self).__init__(*args, **kwargs)

        # we want to be able to submit an empty form as it is part of a page with multiple forms
        # if no user is set, the form is still valid and the save does not change anything
        self.fields['user'].required = False

    def save(self, commit=True):
        # if no user given, just skip it
        if self.cleaned_data['user']:
            instance = super(EventAdminRolesAddForm, self).save(False)
            instance.event = self.event
            if commit:
                instance.save()
            return instance

    def clean_user(self):
        user = self.cleaned_data['user']

        # user already has admin privileges for this event -> invalid
        if user and EventAdminRoles.objects.filter(event=self.event, user=user).exists():
            raise ValidationError(_('User already has permissions for this event assigned'))

        return user


class EventDeleteForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def delete(self):
        self.instance.delete()


class EventArchiveForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    def archive(self):
        # set event flags
        self.instance.archived = True
        self.instance.active = False
        self.instance.save()

        # archive shirt statistics
        if self.instance.ask_shirt:
            shirt_data = {}
            for data in self.instance.helper_set.values('shirt').annotate(num=Count('shirt')).order_by():
                shirt_data[data['shirt']] = data['num']
            EventArchive.objects.create(event=self.instance, key="shirts", version=1, data=shirt_data)

        # delete coordinators and helpers
        for job in self.instance.job_set.all():
            # store number of coordinators
            job.archived_number_coordinators = job.coordinators.count()
            job.save()

            # trigger post_remove signal
            for c in job.coordinators.all():
                job.coordinators.remove(c)

            # now the shifts
            for shift in job.shift_set.all():
                # store number of helpers
                shift.archived_number = shift.helper_set.count()
                shift.save()

                # trigger post_remove signal
                for h in shift.helper_set.all():
                    h.shifts.remove(shift)

        # delete left over badge photos (upload of new file keeps old file)
        # we only want to delete the photos that do not belong to special badges
        event = str(self.instance.pk)
        photos_directory = settings.MEDIA_ROOT / 'private' / event / 'badges' / 'photos'
        try:
            # get all stored images
            all_images = os.listdir(photos_directory)

            # get special badges, that should be kept
            for badge in SpecialBadges.objects.filter(event=self.instance).prefetch_related('template_badge'):
                if badge.template_badge.photo:
                    # if we have a photo, remove it from the all_iamges list
                    cur_image = os.path.basename(badge.template_badge.photo.path)
                    try:
                        all_images.remove(cur_image)
                    except ValueError:
                        pass

            # remove the images now
            for image in all_images:
                os.remove(photos_directory / image)
        except FileNotFoundError:
            pass

        # delete all currently stored log entries - the archive entry will be added afterwards
        LogEntry.objects.filter(event=self.instance).delete()


class EventDuplicateForm(EventForm):
    class Meta:
        model = Event
        fields = ['name', 'url_name', 'date']
        widgets = {
            'date': DatePicker,
        }

    def __init__(self, *args, **kwargs):
        self.other_event = kwargs.pop('other_event')
        self.user = kwargs.pop('user')

        kwargs['instance'] = deepcopy(self.other_event)
        kwargs['instance'].pk = None
        kwargs['instance'].archived = False
        super(EventDuplicateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.active = False

        # prevent post_save hook from adding the needed objects
        activate_badges = self.instance.badges
        activate_gifts = self.instance.gifts
        activate_prerequisites = self.instance.prerequisites
        activate_inventory = self.instance.inventory
        activate_corona = self.instance.corona
        self.instance.badges = False
        self.instance.gifts = False
        self.instance.prerequisites = False
        self.instance.inventory = False
        self.instance.corona = False

        super(EventDuplicateForm, self).save(commit=True)  # we have to save

        # copy logo after save (so that we have a PK)
        if self.instance.logo:
            new_logo = ContentFile(self.instance.logo.read())
            new_logo.name = os.path.basename(self.instance.logo.name)
            self.instance.logo = new_logo

        if self.instance.logo_social:
            new_logo_social = ContentFile(self.instance.logo_social.read())
            new_logo_social.name = os.path.basename(
                self.instance.logo_social.name)
            self.instance.logo_social = new_logo_social

        super(EventDuplicateForm, self).save(commit=True)  # save again

        # remove admins and add current user (done in save)
        self.instance.admins.clear()
        if not self.user.is_superuser:
            self.instance.admins.add(self.user)

        # gifts
        gift_mapping = {}
        gift_set_mapping = {}
        if activate_gifts:
            # duplicate gift settings
            self.other_event.gift_settings.duplicate(self.instance)

            # duplicate all gifts and build mapping
            for gift in self.other_event.gift_set.all():
                new_gift = gift.duplicate(self.instance)
                gift_mapping[gift] = new_gift

            # now duplicate gift sets
            for gift_set in self.other_event.giftset_set.all():
                new_gift_set = gift_set.duplicate(self.instance, gift_mapping)
                gift_set_mapping[gift_set] = new_gift_set

            self.instance.gifts = True
            self.instance.save()

        # prerequisites
        prerequisite_mapping = {}
        if activate_prerequisites:
            for prerequisite in self.other_event.prerequisite_set.all():
                new_prerequisite = prerequisite.duplicate(self.instance)
                prerequisite_mapping[prerequisite] = new_prerequisite

            self.instance.prerequisites = True
            self.instance.save()

        # copy jobs (and shifts)
        for job in self.other_event.job_set.all():
            job.duplicate(self.instance, gift_set_mapping, prerequisite_mapping)

        # badges
        if activate_badges:
            self.other_event.badge_settings.duplicate(self.instance)
            self.instance.badges = True
            self.instance.save()

            for specialbadges in self.other_event.specialbadges_set.all():
                specialbadges.duplicate(self.instance)

        # inventory
        if activate_inventory:
            self.other_event.inventory_settings.duplicate(self.instance)
            self.instance.inventory = True
            self.instance.save()

        # corona
        if activate_corona:
            self.other_event.corona_settings.duplicate(self.instance)
            self.instance.corona = True
            self.instance.save()


class EventMoveForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = []

    new_date = forms.DateField(
        label=_("New date"),
        widget=DatePicker,
    )

    def save(self, commit=True):
        new_date = self.cleaned_data.get('new_date')
        diff_days = new_date - self.instance.date

        if self.instance.date != new_date:
            # change date of every shift
            for job in self.instance.job_set.all():
                for shift in job.shift_set.all():
                    shift.move_date(new_date)
                    shift.save()

            # change event date
            self.instance.date = new_date

            # change 'changes_until' if set
            if self.instance.changes_until:
                self.instance.changes_until += diff_days

            self.instance.save()

        return self.instance


class PastEventForm(forms.Form):
    months = forms.IntegerField(
        min_value=0,
        label=_("Months"),
    )
