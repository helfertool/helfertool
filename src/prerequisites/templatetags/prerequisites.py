from django import template
from prerequisites.models import FulfilledPrerequisite

register = template.Library()


@register.simple_tag
def helper_has_fulfilled_prerequisite(helper, prerequisite):
    return prerequisite.check_helper(helper)
