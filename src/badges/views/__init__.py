from .settings import settings, settings_advanced, default_template, current_template
from .permission import edit_permission, delete_permission
from .role import edit_role, delete_role
from .design import edit_design, delete_design, get_design_bg
from .generate import index, generate, warnings, failed, download, tasklist
from .register import register
from .badge import edit_badge, get_badge_photo
from .specialbadges import list_specialbadges, edit_specialbadges, edit_specialbadges_template, delete_specialbadges, \
    get_specialbadges_photo
