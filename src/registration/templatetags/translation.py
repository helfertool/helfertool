from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def translated_field(form, name, lang):
    return form["{}_{}".format(name, lang)]