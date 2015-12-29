from django.conf.urls import url

from . import views

urlpatterns = [
    #
    # configuration
    #

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/$',
        views.configure_badges,
        name='configure_badges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/settings/',
        views.edit_badgesettings,
        name='badgesettings'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/permission/'
        '(?P<permission_pk>[0-9]+)/$',
        views.edit_badgepermission,
        name='edit_badgepermission'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/permission/add/',
        views.edit_badgepermission,
        name='new_badgepermission'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/role/'
        '(?P<role_pk>[0-9]+)/$',
        views.edit_badgerole,
        name='edit_badgerole'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/role/add/',
        views.edit_badgerole,
        name='new_badgerole'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/design/'
        '(?P<design_pk>[0-9]+)/$',
        views.edit_badgedesign,
        name='edit_badgedesign'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/design/add/',
        views.edit_badgedesign,
        name='new_badgedesign'),

    #
    # badge generation
    #

    # overview page
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/$',
        views.badges,
        name='badges'),

    # show warnings
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/'
        '(?P<job_pk>[0-9]+)/warnings/$',
        views.badges_warnings,
        name='badges_warnings'),

    # generate for job
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/'
        '(?P<job_pk>[0-9]+)/$',
        views.generate_badges,
        name='generate_job_badges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/'
        '(?P<job_pk>[0-9]+)/all/$',
        views.generate_badges,
        {'generate_all': True},
        name='generate_all_job_badges'),

    # generate for all jobs
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/alljobs/$',
        views.generate_badges,
        name='generate_badges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/alljobs/all/$',
        views.generate_badges,
        {'generate_all': True},
        name='generate_all_badges'),

    # register badges
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/register/',
        views.register_badge,
        name='register_badge'),
]
