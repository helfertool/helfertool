from django.conf.urls import url

from . import views

app_name = 'badges'
urlpatterns = [
    #
    # settings
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/settings/$',
        views.settings,
        name='settings'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/settings/advanced',
        views.settings_advanced,
        name='settings_advanced'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/defaulttemplate',
        views.default_template,
        name='default_template'),

    #
    # edit badge
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/(?P<helper_pk>[0-9a-f\-]+)/badge/$',
        views.edit_badge,
        name='edit_badge'),

    #
    # permission
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/permission/(?P<permission_pk>[0-9]+)/$',
        views.edit_permission,
        name='edit_permission'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/permission/add/',
        views.edit_permission,
        name='new_permission'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/permission/(?P<permission_pk>[0-9]+)/delete/$',
        views.delete_permission,
        name='delete_permission'),

    #
    # role
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/role/(?P<role_pk>[0-9]+)/$',
        views.edit_role,
        name='edit_role'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/role/add/',
        views.edit_role,
        name='new_role'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/role/(?P<role_pk>[0-9]+)/delete/$',
        views.delete_role,
        name='delete_role'),

    #
    # design
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/design/(?P<design_pk>[0-9]+)/$',
        views.edit_design,
        name='edit_design'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/design/add/',
        views.edit_design,
        name='new_design'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/design/(?P<design_pk>[0-9]+)/delete/$',
        views.delete_design,
        name='delete_design'),

    #
    # badge generation
    #

    # overview page
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/$',
        views.index,
        name='index'),

    # overview of generated badges (list of tasks)
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/tasklist/$',
        views.tasklist,
        name='tasklist'),

    # warnings
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/warnings/(?P<job_pk>[0-9]+)$',
        views.warnings,
        name='warnings'),

    # generate for job
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/(?P<job_pk>[0-9]+)/$',
        views.generate,
        {'generate': 'job'},
        name='generate_for_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/(?P<job_pk>[0-9]+)/all/$',
        views.generate,
        {'generate': 'job', 'skip_printed': False},
        name='generate_all_for_job'),

    # generate special badges
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/special/$',
        views.generate,
        {'generate': 'special'},
        name='generate_special'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/special/all/$',
        views.generate,
        {'generate': 'special', 'skip_printed': False},
        name='generate_all_special'),

    # generate for all jobs and special badges
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/$',
        views.generate,
        {'generate': 'all'},
        name='generate'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/all/$',
        views.generate,
        {'generate': 'all', 'skip_printed': False},
        name='generate_all'),

    # failed page
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/failed/'
        r'(?P<task_id>[a-z0-9\-]+)/$',
        views.failed,
        name='failed'),

    # download badges
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/download/'
        r'(?P<task_id>[a-z0-9\-]+)/$',
        views.download,
        name='download'),

    #
    # register badges
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/register/',
        views.register,
        name='register'),

    #
    # special badges
    #
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/special/$',
        views.list_specialbadges,
        name='list_specialbadges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/special/(?P<specialbadges_pk>[0-9]+)/$',
        views.edit_specialbadges,
        name='edit_specialbadges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/special/add/$',
        views.edit_specialbadges,
        name='new_specialbadges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/special/(?P<specialbadges_pk>[0-9]+)/template/$',
        views.edit_specialbadges_template,
        name='edit_specialbadges_template'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/special/(?P<specialbadges_pk>[0-9]+)/delete/$',
        views.delete_specialbadges,
        name='delete_specialbadges'),
]
