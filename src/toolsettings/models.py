from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prose_editor.fields import ProseEditorField
from helfertool.utils import PROSE_EDITOR_DEFAULT_EXTENSIONS


class AbstractSetting(models.Model):
    """
    All types of settings have a key
    """

    class Meta:
        abstract = True

    key = models.CharField(
        max_length=200,
        primary_key=True,
        validators=[RegexValidator("^[a-zA-Z0-9]+$")],
        verbose_name=_("Key"),
    )

    def __str__(self):
        return self.key


class HTMLSetting(AbstractSetting):
    value = ProseEditorField(
        extensions=PROSE_EDITOR_DEFAULT_EXTENSIONS,
        sanitize=True,
        blank=True,
        default="",
        verbose_name=_("HTML"),
    )


class TextSetting(AbstractSetting):
    value = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Text"),
    )
