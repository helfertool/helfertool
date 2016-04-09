from __future__ import absolute_import

from celery import shared_task

from django.conf import settings
from django.utils import translation

from PIL import Image

import os
import shutil

import badges.creator
import registration


@shared_task
def scale_badge_photo(filepath):
    img = Image.open(filepath)
    img.thumbnail((settings.BADGE_PHOTO_MAX_SIZE,
                   settings.BADGE_PHOTO_MAX_SIZE))
    img.save(filepath)

@shared_task
def generate_badges(event_pk, job_pk, skip_printed):
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

    # jobs that should be handled
    if job:
        jobs = [job, ]
        filename = job.name
    else:
        jobs = event.job_set.all()
        filename = event.name

    # add helpers and coordinators
    for j in jobs:
        for h in j.helpers_and_coordinators():
            # skip if badge was printed already
            # (and this behaviour is requested)
            if skip_printed and h.badge.printed:
                continue

            helpers_job = h.badge.get_job()
            # print badge only if this is the primary job or the job is
            # unambiguous
            if (not helpers_job or helpers_job == j):
                creator.add_helper(h)
    try:
        tmp_dir, pdf_filename = creator.generate()
    except Exception as e:
        creator.finish()
        raise e
    finally:
        translation.activate(prev_language)

    clean = cleanup.subtask((tmp_dir, ),
                            countdown=settings.BADGE_PDF_TIMEOUT)
    cleanup_task = clean.delay()

    return pdf_filename, filename, cleanup_task.task_id

@shared_task(bind=True)
def cleanup(self, tmp_dir):
    # wait for BADGE_RM_DELAY seconds and then really delete the files
    rm = cleanup_rm.subtask((tmp_dir, ),
                            countdown=settings.BADGE_RM_DELAY)
    cleanup_task = rm.delay()

@shared_task
def cleanup_rm(tmp_dir):
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
