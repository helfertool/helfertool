from django import template
from django.conf import settings
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from ..models import HTMLSetting, TextSetting
from ..utils import get_setting

register = template.Library()


@register.simple_tag(takes_context=True)
def htmlsetting(context, key):
    return mark_safe(get_setting(HTMLSetting, key, ""))


@register.simple_tag(takes_context=True)
def textsetting(context, key):
    return get_setting(TextSetting, key, "")
