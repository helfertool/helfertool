from django import template

register = template.Library()


@register.assignment_tag
def badge_job_design_field(form, job_pk):
    return form['job_%d_design' % job_pk]


@register.assignment_tag
def badge_job_role_field(form, job_pk):
    return form['job_%d_role' % job_pk]
