from django import template
from django.forms.renderers import get_default_renderer
from django.template.defaultfilters import date
from django.template.exceptions import TemplateSyntaxError
from django.utils.safestring import mark_safe

register = template.Library()
renderer = get_default_renderer()


@register.tag
def shifttable(parser, token):
    """Renders a table-like view of shifts for a specific job.
    The rendered shifts can be restricted by specifying a list of shifts.

    Example 1:

        {% shifttable job %}
            {{ shift.time_hours }}
        {% endshifttable %}

    Example 2:

        {% shifttable job visible_shifts %}
            {{ shift.time_hours }}
        {% endshifttable %}

    The content inside the tag is rendered for every shift.
    """
    # parse parameters in opening tag
    bits = token.split_contents()
    if len(bits) not in [2, 3]:
        raise TemplateSyntaxError("'shifttable' statements require a job and optionally a list of shifts")

    job_name = bits[1]

    if len(bits) == 3:
        shifts_name = bits[2]
    else:
        shifts_name = None

    # parse until endshifttable
    nodelist = parser.parse(("endshifttable",))
    parser.delete_first_token()
    return ShiftTableNode(job_name, shifts_name, nodelist)


class ShiftTableNode(template.Node):
    """Implementation of 'shifttable` tag, see `shifttable`."""

    def __init__(self, job_name, shifts_name, nodelist):
        self.job_name = job_name
        self.shifts_name = shifts_name
        self.nodelist = nodelist

    def render(self, context):
        # get job from context (based on name given as parameter)
        job = context[self.job_name]
        if self.shifts_name:
            shifts = context[self.shifts_name]
        else:
            shifts = None

        # render single days
        days_html = []
        for day, shifts in job.shifts_by_day(shifts).items():
            days_html.append(self._render_day(context, day, shifts))

        # put it together with frame
        template = '<div class="shifttable">{}</div>'
        return template.format("".join(days_html))

    def _render_day(self, context, day, shifts):
        # render all shifts
        shifts_html = []
        for shift in shifts:
            shifts_html.append(self._render_shift(context, shift))

        # put it together with date
        template = '<div class="shifttable-day"><div class="shifttable-date">{}</div>{}</div>'
        day_str = date(day)
        return template.format(day_str, "".join(shifts_html))

    def _render_shift(self, context, shift):
        # render content for single shift
        context["shift"] = shift
        html = self.nodelist.render(context)
        return '<div class="shifttable-shift">{}</div>'.format(html)


@register.simple_tag
def form_shifttable(field):
    """Renders a table-like view of shifts for a form field.

    The widget of the form field must be:
    - ShiftTableWidget
    - ShiftTableRegistrationWidget

    Example:

        {% form_shifttable form.shifts %}

    Explanation: If we would just modify the widget, we cannot get access to the model, i.e. to the jobs and shifts.
    The widget only sees IDs and labels, nothing more.

    Therefore, this template tag first works on the model data and then fetchs the context for rendering from
    the widget. We therefore have a similar situation in the template as if we would directly modify the template
    of the widget. So we are close to the widget rendering of Django, but can group the fields based on jobs and days.
    """
    # get all possible shifts (= the queryset):
    shifts = field.field.queryset

    # group shifts by job (we assume that all shifts belong to the same event)
    jobs_and_shifts = {}
    for shift in shifts:
        job = shift.job
        if job in jobs_and_shifts:
            jobs_and_shifts[job].append(shift)
        else:
            jobs_and_shifts[job] = [
                shift,
            ]

    # for rendering, we first need the widget
    widget = field.field.widget

    # build context using the widget and add custom things
    # note: custom attrs not passed here
    context = widget.get_context(field.name, field.value(), {})

    # flatten the optgroups, so that we can do a direct lookup in form_shifttable_shift with the pk of the shift
    context["widget"]["options"] = {}
    for group in context["widget"]["optgroups"]:
        for option in group[1]:
            # option["value"] is a ModelChoiceIteratorValue object
            pk = option["value"].value
            context["widget"]["options"][pk] = option

    # add the prepared list of jobs and shifts to the context
    context["jobs"] = jobs_and_shifts

    # render the template specified in the widget. it uses the shifttable tag to render the table
    return mark_safe(renderer.render(widget.template_name, context))


@register.simple_tag
def form_shifttable_shift(widget, shift):
    """Belongs to form_shifttable and is called from the template, that is rendered there.
    It renders the input for one shift using the template "option_template_name" from the widget."""
    shiftwidget = widget["options"][shift.pk]

    context = {
        "widget": shiftwidget,
        "shift": shift,
        "event": shift.job.event,
    }
    return mark_safe(renderer.render(shiftwidget["template_name"], context))


@register.simple_tag
def form_shifttable_shift_registration(widget, shift):
    """Same as form_shifttable, but disables shifts if registration should not be possible."""
    shiftwidget = widget["options"][shift.pk]

    if shift.is_full():
        shiftwidget["attrs"]["disabled"] = True

    if shift.blocked and widget["respect_blocked"]:
        shiftwidget["attrs"]["disabled"] = True

    context = {
        "widget": shiftwidget,
        "shift": shift,
        "event": shift.job.event,
    }
    return mark_safe(renderer.render(shiftwidget["template_name"], context))


@register.inclusion_tag("registration/templatetags/shift_progress.html")
def shift_progress(shift, highlight_missing=False):
    """Renders a progress bar to visualize the number of registered and missing helpers.

    If `highlight_missing` is True, the registered helpers are green and the missing ones red/yellow.
    Otherwise, the registered helpers are green/yellow/red and the missing ones gray.
    """
    percent = shift.helpers_percent()
    percent_vacant = 100 - percent

    context = {
        "highlight_missing": highlight_missing,
        "percent": percent,
        "percent_vacant": percent_vacant,
    }
    return context
