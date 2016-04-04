from __future__ import absolute_import

from celery import shared_task
from PIL import Image

from django.conf import settings


@shared_task
def scale_badge_photo(filepath):
    img = Image.open(filepath)
    img.thumbnail((settings.BADGE_PHOTO_MAX_SIZE,
                   settings.BADGE_PHOTO_MAX_SIZE))
    img.save(filepath)
