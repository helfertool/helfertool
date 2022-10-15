from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import os


class RestrictedImageField(models.ImageField):
    """ImageField that restricts the file extensions to jpg, jpeg and png.

    For example, LaTeX does not like some file extensions that users could upload."""

    def validate(self, value, model_instance):
        super().validate(value, model_instance)

        ext = os.path.splitext(value.name)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            raise ValidationError(_("File type not supported, use JPG or PNG."))
