from django import template

register = template.Library()


@register.filter
def duration_hours(td):
    return int(td.total_seconds()) // 3600
