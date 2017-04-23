from django import template

register = template.Library()


@register.filter
def lookup_shift(h, key):
    return h['shift_' + str(key)]


@register.simple_tag
def get_jobs(form):
    return form.get_jobs()


@register.simple_tag
def get_shifts(form, job):
    return form.get_shifts(job)
