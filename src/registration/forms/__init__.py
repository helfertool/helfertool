from .event import EventForm, EventDeleteForm, EventArchiveForm, \
    EventDuplicateForm, EventMoveForm
from .job import JobForm, JobDeleteForm, JobDuplicateForm, JobDuplicateDayForm, JobSortForm
from .shift import ShiftForm, ShiftDeleteForm
from .helper import HelperForm, HelperDeleteForm, \
    HelperDeleteCoordinatorForm, HelperAddShiftForm, \
    HelperAddCoordinatorForm, HelperSearchForm, HelperResendMailForm
from .link import LinkForm, LinkDeleteForm
from .registration import RegisterForm, DeregisterForm
from .duplicates import MergeDuplicatesForm
