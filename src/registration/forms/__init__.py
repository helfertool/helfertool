from .event import EventForm, EventAdminRolesForm, EventAdminRolesAddForm, EventDeleteForm, EventArchiveForm, \
    EventDuplicateForm, EventMoveForm, PastEventForm
from .job import JobForm, JobAdminRolesForm, JobAdminRolesAddForm, JobDeleteForm, JobDuplicateForm, \
    JobDuplicateDayForm, JobSortForm
from .shift import ShiftForm, ShiftDeleteForm
from .helper import HelperForm, HelperDeleteForm, HelperDeleteCoordinatorForm, HelperAddShiftForm, \
    HelperAddCoordinatorForm, HelperSearchForm, HelperResendMailForm, HelperInternalCommentForm
from .link import LinkForm, LinkDeleteForm
from .registration import RegisterForm, DeregisterForm
from .duplicates import MergeDuplicatesForm
from .widgets import SingleHelperSelectWidget