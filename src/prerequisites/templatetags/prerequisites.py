from django import template
from prerequisites.models import FulfilledPrerequisite

register = template.Library()


@register.simple_tag
def helper_has_fulfilled_prerequisite(helper, prerequisite):
    # See whether helper has fulfilled prerequisite, if exists
    try:
        fulfilled = FulfilledPrerequisite.objects.all().get(prerequisite=prerequisite, helper=helper)
        return fulfilled.has_prerequisite
    except FulfilledPrerequisite.DoesNotExist:
        return False
