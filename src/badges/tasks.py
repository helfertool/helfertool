from __future__ import absolute_import

from celery import shared_task
from celery.exceptions import Ignore

from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _

from PIL import Image

import os
import shutil

import badges
import badges.creator
import registration


@shared_task
def scale_badge_photo(filepath):
    img = Image.open(filepath)
    img.thumbnail((settings.BADGE_PHOTO_MAX_SIZE, settings.BADGE_PHOTO_MAX_SIZE))
    img.save(filepath)


@shared_task(bind=True, throws=(badges.creator.BadgeCreatorError,))
def generate_badges(self, event_pk, job_pk, generate, skip_printed):
    event = registration.models.Event.objects.get(pk=event_pk)
    try:
        job = registration.models.Job.objects.get(pk=job_pk)
    except registration.models.Job.DoesNotExist:
        job = None

    # set language
    prev_language = translation.get_language()
    translation.activate(event.badgesettings.language)

    # badge creation
    creator = badges.creator.BadgeCreator(event.badge_settings)

    # determine the jobs, that will be included, and the filename
    if generate == "job" and job:
        jobs = [
            job,
        ]
        filename = job.name
    elif generate == "special":
        jobs = []
        filename = _("Special badges")
    elif generate == "all":
        jobs = event.job_set.all()
        filename = event.name
    else:
        raise ValueError("Invalid parameters")

    # add helpers and coordinators from selected jobs
    for j in jobs:
        for h in j.helpers_and_coordinators():
            # skip if badge was printed already
            # (and this behaviour is requested)
            if skip_printed and h.badge.printed:
                continue

            helpers_job = h.badge.get_job()
            # print badge only if this is the primary job or the job is
            # unambiguous
            if not helpers_job or helpers_job == j:
                # skip helpers if this is requested
                if event.badge_settings.only_coordinators and not h.is_coordinator:
                    continue

                creator.add_badge(h.badge)

    # add special badges
    if generate == "special" or generate == "all":
        for b in badges.models.Badge.objects.filter(event=event, helper=None):
            if not (skip_printed and b.printed):
                creator.add_badge(b)

    # try to generate the pdf file
    try:
        tmp_dir, pdf_filename = creator.generate()
    except badges.creator.BadgeCreatorError as e:
        creator.finish()
        self.update_state(state="CREATOR_ERROR", meta={"error": e.value, "latex_output": e.latex_output})
        raise Ignore()
    finally:
        translation.activate(prev_language)

    # schedule cleanup task
    clean = cleanup.subtask((tmp_dir,), countdown=settings.BADGE_PDF_TIMEOUT + settings.BADGE_RM_DELAY)
    cleanup_task = clean.delay()

    return pdf_filename, filename, cleanup_task.task_id


@shared_task
def cleanup(tmp_dir):
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
