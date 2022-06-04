from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from ..models import HTMLSetting, TextSetting
from ..utils import get_setting

register = template.Library()


@register.simple_tag
def htmlsetting(key):
    """Return HTML setting from database."""
    return mark_safe(get_setting(HTMLSetting, key, ""))


@register.simple_tag
def textsetting(key):
    """Return text setting from database."""
    return get_setting(TextSetting, key, "")


@register.simple_tag
def djangosetting(name):
    """Return setting from Django configuration."""
    return getattr(settings, name, "")
