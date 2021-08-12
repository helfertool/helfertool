from django.conf import settings
from django.core.management.base import BaseCommand

import os
import shutil

from registration.models.event import Event, _logo_upload_path
from badges.models.badge import Badge, _badge_upload_path
from badges.models.design import BadgeDesign, _design_upload_path
from badges.models.settings import BadgeSettings, _settings_upload_path


def handle_field(instance, fieldname, upload_to_func, dest):
    field = getattr(instance, fieldname)

    # check if there is a file
    if field:
        # is it already in public / private?
        if not field.name.startswith(dest):
            print("Moving {}".format(field.name))

            # determine new name
            new_name = upload_to_func(instance, os.path.basename(field.name))
            new_path = settings.MEDIA_ROOT / new_name

            # rename file and first make sure that directory exists
            os.makedirs(os.path.dirname(new_path), settings.FILE_UPLOAD_DIRECTORY_PERMISSIONS, exist_ok=True)
            try:
                shutil.copy(field.path, new_path)
            except FileNotFoundError:
                print("WARNING: File not found: {}".format(field.name))
                return

            # set new name in DB
            field.name = new_name


class Command(BaseCommand):
    help = 'Moves all uploaded files to the new directories (migration to Helfertool version 2.0.x)'

    def handle(self, *args, **options):
        # model: Event
        for event in Event.objects.all():
            handle_field(event, "logo", _logo_upload_path, "public")
            handle_field(event, "logo_social", _logo_upload_path, "public")
            event.save()

        # model: Badge
        for badge in Badge.objects.all():
            handle_field(badge, "photo", _badge_upload_path, "private")
            badge.save()

        # model: BadgeDesign
        for design in BadgeDesign.objects.all():
            handle_field(design, "bg_front", _design_upload_path, "private")
            handle_field(design, "bg_back", _design_upload_path, "private")
            design.save()

        # model: BadgeSettings
        for setting in BadgeSettings.objects.all():
            handle_field(setting, "latex_template", _settings_upload_path, "private")
            setting.save()

        # delete old directories (including files, which do not belong to an existing model)
        shutil.rmtree(settings.MEDIA_ROOT / "logos", ignore_errors=True)
        shutil.rmtree(settings.MEDIA_ROOT / "badges", ignore_errors=True)
