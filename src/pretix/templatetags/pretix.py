from django import template

register = template.Library()


@register.simple_tag
def pretix_job_item_field(form, job_pk):
    return form["job_%d_item" % job_pk]
