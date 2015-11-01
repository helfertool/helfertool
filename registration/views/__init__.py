from .registration import index, form, registered, validate

from .admin import admin, jobs_and_shifts, add_user, coordinators, statistics
from .event import edit_event, delete_event
from .job import edit_job, delete_job
from .shift import edit_shift, delete_shift
from .helper import helpers, add_helper, edit_helper, delete_helper, \
    add_coordinator, delete_coordinator
from .link import links, edit_link, delete_link
from .badge import configure_badges, edit_badgedesign, edit_badgesettings, \
    edit_badgepermission, edit_badgerole, badges, generate_badges, \
    badges_warnings, register_badge
from .export import export
from .permissions import permissions, delete_permission
from .mail import mail
