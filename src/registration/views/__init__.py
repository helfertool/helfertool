from .registration import index, form, registered, validate, deregister, \
    deleted, update_personal

from .admin import admin, jobs_and_shifts, add_user, coordinators
from .event import edit_event, delete_event, archive_event, duplicate_event
from .job import edit_job, delete_job, duplicate_job, sort_job
from .shift import edit_shift, delete_shift
from .helper import helpers, add_helper, edit_helper, delete_helper, \
    add_coordinator, delete_coordinator, add_helper_to_shift, \
    add_helper_as_coordinator, search_helper, view_helper, resend_mail
from .link import links, edit_link, delete_link
from .export import export
from .permissions import permissions, delete_permission
from .account import change_user
from .duplicates import duplicates, merge
