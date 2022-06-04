from .registration import index_all_events, index, form, registered, validate, deregister, deleted, update_personal
from .admin import admin, jobs_and_shifts, coordinators
from .event import (
    edit_event,
    edit_event_admins,
    delete_event,
    archive_event,
    duplicate_event,
    move_event,
    past_events,
    get_event_logo,
)
from .job import edit_job, edit_job_admins, delete_job, duplicate_job, duplicate_job_day, sort_job
from .shift import edit_shift, delete_shift
from .helper import (
    helpers,
    helpers_for_job,
    add_helper,
    edit_helper,
    delete_helper,
    add_coordinator,
    delete_coordinator,
    add_helper_to_shift,
    add_helper_as_coordinator,
    search_helper,
    view_helper,
    resend_mail,
)
from .link import links, edit_link, delete_link
from .export import export
from .duplicates import duplicates, merge
from .vacant import vacant_shifts
