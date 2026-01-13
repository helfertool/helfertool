from .models import Event, EventAdminRoles, Job, JobAdminRoles, Helper

# This is the central file that defines and manages the different permissions for events, jobs and users.
# Global permissions like creating events, users or sending newsletters are managed in the accounts app.

# There are different roles, defined in registration.models.EventAdminRoles and registration.models.JobAdminRoles

# In the views, a certain access is requested.
ACCESS_INVOLVED = "ACCESS_INVOLVED"  # basically just the main page (user is somehow involved, necessary for all roles)
ACCESS_EVENT_EDIT = "ACCESS_EVENT_EDIT"  # edit/archive/delete the event
ACCESS_EVENT_EDIT_LINKS = "ACCESS_EVENT_EDIT_LINKS"  # edit links of an event
ACCESS_EVENT_EDIT_JOBS = "ACCESS_EVENT_EDIT_JOBS"  # add/delete/duplicate/sort jobs
ACCESS_EVENT_EXPORT_HELPERS = "ACCESS_EVENT_EXPORT_HELPERS"  # export data as pdf/excel
ACCESS_EVENT_EDIT_DUPLICATES = "ACCESS_EVENT_EDIT_DUPLICATES"  # manage duplicated helpers
ACCESS_EVENT_VIEW_COORDINATORS = "ACCESS_EVENT_VIEW_COORDINATORS"  # view the contact details of coordinators
ACCESS_EVENT_VIEW_AUDITLOGS = "ACCESS_EVENT_VIEW_AUDITLOGS"  # view audit logs of the event

ACCESS_JOB_EDIT = "ACCESS_JOB_EDIT"  # edit an existing job
ACCESS_JOB_EDIT_HELPERS = "ACCESS_JOB_EDIT_HELPERS"  # add/remove helpers of job
ACCESS_JOB_VIEW_HELPERS = "ACCESS_JOB_VIEW_HELPERS"  # view helpers of job

ACCESS_HELPER_EDIT = "ACCESS_HELPER_EDIT"  # edit helper data without sensitive data
ACCESS_HELPER_VIEW = "ACCESS_HELPER_VIEW"  # view helper data without sensitive data
ACCESS_HELPER_EDIT_SENSITIVE = "ACCESS_HELPER_EDIT_SENSITIVE"  # edit helper data including sensitive data
ACCESS_HELPER_VIEW_SENSITIVE = "ACCESS_HELPER_VIEW_SENSITIVE"  # view helper data including sensitive data
ACCESS_HELPER_INTERNAL_COMMENT_EDIT = "ACCESS_HELPER_INTERNAL_COMMENT_EDIT"  # edit the internal comment of a helper
ACCESS_HELPER_INTERNAL_COMMENT_VIEW = "ACCESS_HELPER_INTERNAL_COMMENT_VIEW"  # view the internal comment of a helper
ACCESS_HELPER_RESEND = "ACCESS_HELPER_RESEND"  # resend the confirmation mail to a helper

ACCESS_INVENTORY_EDIT = "ACCESS_INVENTORY_EDIT"  # edit inventory settings for an event
ACCESS_INVENTORY_HANDLE = "ACCESS_INVENTORY_HANDLE"  # register and take back inventory

ACCESS_BADGES_EDIT = "ACCESS_BADGES_EDIT"  # edit badge settings for an event
ACCESS_BADGES_EDIT_HELPER = "ACCESS_BADGES_EDIT_HELPER"  # edit badges of single helpers
ACCESS_BADGES_EDIT_SPECIAL = "ACCESS_BADGES_EDIT_SPECIAL"  # edit special badges (=badges without helpers)
ACCESS_BADGES_GENERATE = "ACCESS_BADGES_GENERATE"  # generate and register badges

ACCESS_MAILS_SEND = "ACCESS_MAILS_SEND"  # can send mails
ACCESS_MAILS_VIEW = "ACCESS_MAILS_VIEW"  # can view mails

ACCESS_STATISTICS_VIEW = "ACCESS_STATISTICS_VIEW"  # can view statistics (shirts & nutrition)

ACCESS_GIFTS_EDIT = "ACCESS_GIFTS_EDIT"  # edit gift settings for an event
ACCESS_GIFTS_HANDLE_GIFTS = "ACCESS_GIFTS_HANDLE_GIFTS"  # give gifts to helpers
ACCESS_GIFTS_HANDLE_PRESENCE = "ACCESS_GIFTS_HANDLE_PRESENCE"  # change presence of helpers
ACCESS_GIFTS_VIEW_SUMMARY = "ACCESS_GIFTS_VIEW_SUMMARY"  # view summary of gift data (collected deposit, missing shirts)

ACCESS_PREREQUISITES_EDIT = "ACCESS_PREREQUISITES_EDIT"  # edit prerequisite settings for an event
ACCESS_PREREQUISITES_VIEW = "ACCESS_PREREQUISITES_VIEW"  # view global lists which helper fulfils which prerequisites
ACCESS_PREREQUISITES_HANDLE = "ACCESS_PREREQUISITES_HANDLE"  # set for helpers whether they fulfil prerequisites

# Based on requested access and role, we can decide whether we grant access or not.
# Here, for each access type, the allowed/required roles are listed (on event and job level)
_rbac_matrix = {
    ACCESS_INVOLVED: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
            EventAdminRoles.ROLE_INVENTORY,
            EventAdminRoles.ROLE_BADGES,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_EVENT_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_EVENT_EDIT_LINKS: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_EVENT_EDIT_JOBS: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_EVENT_EXPORT_HELPERS: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_EVENT_EDIT_DUPLICATES: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [],
    ],
    ACCESS_EVENT_VIEW_COORDINATORS: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
            EventAdminRoles.ROLE_INVENTORY,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_EVENT_VIEW_AUDITLOGS: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_JOB_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_JOB_EDIT_HELPERS: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_JOB_VIEW_HELPERS: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
            EventAdminRoles.ROLE_INVENTORY,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_HELPER_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_HELPER_VIEW: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
            EventAdminRoles.ROLE_INVENTORY,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_HELPER_EDIT_SENSITIVE: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
        ],
    ],
    ACCESS_HELPER_VIEW_SENSITIVE: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
            EventAdminRoles.ROLE_INVENTORY,
        ],
        [
            JobAdminRoles.ROLE_FULL,
        ],
    ],
    ACCESS_HELPER_INTERNAL_COMMENT_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_HELPER_INTERNAL_COMMENT_VIEW: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
            EventAdminRoles.ROLE_INVENTORY,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_HELPER_RESEND: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_INVENTORY_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_INVENTORY_HANDLE: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_INVENTORY,
        ],
        [],
    ],
    ACCESS_BADGES_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_BADGES_EDIT_HELPER: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [],
    ],
    ACCESS_BADGES_EDIT_SPECIAL: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [],
    ],
    ACCESS_BADGES_GENERATE: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_BADGES,
        ],
        [],
    ],
    ACCESS_MAILS_SEND: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_MAILS_VIEW: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_STATISTICS_VIEW: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
    ACCESS_GIFTS_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_GIFTS_HANDLE_GIFTS: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
            EventAdminRoles.ROLE_FRONTDESK,
        ],
        [],
    ],
    ACCESS_GIFTS_HANDLE_PRESENCE: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [],
    ],
    ACCESS_GIFTS_VIEW_SUMMARY: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [],
    ],
    ACCESS_PREREQUISITES_EDIT: [
        [
            EventAdminRoles.ROLE_ADMIN,
        ],
        [],
    ],
    ACCESS_PREREQUISITES_VIEW: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [],
    ],
    ACCESS_PREREQUISITES_HANDLE: [
        [
            EventAdminRoles.ROLE_ADMIN,
            EventAdminRoles.ROLE_RESTRICTED_ADMIN,
        ],
        [
            JobAdminRoles.ROLE_FULL,
            JobAdminRoles.ROLE_DEFAULT,
        ],
    ],
}


def has_access(user, resource, access):
    """
    Checks whether the user has access to the resource with the requested access type.
    """
    # No user, no permissions
    if not user.is_authenticated:
        return False

    # superuser can do anything
    if user.is_superuser:
        return True

    # check type of accessed resource
    if isinstance(resource, Event):
        return _has_access_event(user, resource, access)
    elif isinstance(resource, Job):
        return _has_access_job(user, resource, access)
    elif isinstance(resource, Helper):
        return _has_access_helper(user, resource, access)
    else:
        raise ValueError("Invalid resource type")


def has_access_event_or_job(user, event, access):
    """
    Checks whether the user has access to the event or to any job of the event.
    """
    # check event
    if has_access(user, event, access):
        return True

    # check jobs
    for job in event.job_set.all():
        if has_access(user, job, access):
            return True

    return False


def _has_access_event(user, event, access):
    # check role
    if _check_event_role(user, event, access):
        return True

    # special cases
    if access == ACCESS_INVOLVED:
        # involved: also check jobs
        for job in event.job_set.all():
            if _check_job_role(user, job, access):
                return True

    # nothing worked, no access
    return False


def _has_access_job(user, job, access):
    # check role
    if _check_event_role(user, job.event, access):
        return True

    # handle job admins
    if _check_job_role(user, job, access):
        return True

    return False


def _has_access_helper(user, helper, access):
    # check role
    if _check_event_role(user, helper.event, access):
        return True

    # handle job admins for helpers
    for shift in helper.shifts.all():
        if _check_job_role(user, shift.job, access):
            return True

    # handle job admins for coordinators
    for job in helper.job_set.all():
        if _check_job_role(user, job, access):
            return True

    return False


def _check_event_role(user, event, access):
    """
    Check whether the user has a required role for this access on the event level.
    """
    # get admin roles of user
    try:
        admin_roles = EventAdminRoles.objects.get(event=event, user=user).roles
    except EventAdminRoles.DoesNotExist:
        return False

    # and check the rbac matrix
    return _check_role_matrix(access, 0, admin_roles)


def _check_job_role(user, job, access):
    """
    Check whether the user has a required role for this access on the job level.
    """
    # get job admin roles of user
    try:
        admin_roles = JobAdminRoles.objects.get(job=job, user=user).roles
    except JobAdminRoles.DoesNotExist:
        return False

    # and check the rbac matrix
    return _check_role_matrix(access, 1, admin_roles)


def _check_role_matrix(access, matrix_offset, assigned_roles):
    # get required roles for this access type
    try:
        required_roles = _rbac_matrix[access][matrix_offset]
    except KeyError:
        return False

    # check if we have one of the required roles. then we are done
    for role in assigned_roles:
        if role in required_roles:
            return True

    return False
