from .event import EventForm, EventDeleteForm, EventArchiveForm, \
    EventDuplicateForm
from .job import JobForm, JobDeleteForm, JobDuplicateForm
from .shift import ShiftForm, ShiftDeleteForm
from .helper import HelperForm, HelperDeleteForm, \
    HelperDeleteCoordinatorForm, HelperAddShiftForm, \
    HelperAddCoordinatorForm, HelperSearchForm
from .link import LinkForm, LinkDeleteForm
from .registration import RegisterForm
from .delete import DeleteForm
from .user import UsernameForm, CreateUserForm
from .duplicates import MergeDuplicatesForm
