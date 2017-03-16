from django import template

register = template.Library()

@register.filter
def duration_hours(td):
    total_seconds = int(td.total_seconds())
    return int(td.total_seconds()) // 3600
