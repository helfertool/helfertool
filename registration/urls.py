from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # login, logout
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html'},
        name='login'),

    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='logout'),

    # admin interface
    url(r'^admin/$',
        views.admin,
        name='admin'),

    url(r'^admin/new/$',
        views.edit_event,
        name='new_event'),

    url(r'^admin/user/$',
        views.add_user,
        name='add_user'),

    url(r'^admin/permissions/$',
        views.permissions,
        name='permissions'),

    url(r'^admin/permissions/(?P<user_pk>[0-9]+)/event/delete/$',
        views.delete_permission, {'groupname': settings.GROUP_ADDUSER},
        name='delete_user_permission'),

    url(r'^admin/permissions/(?P<user_pk>[0-9]+)/user/delete/$',
        views.delete_permission, {'groupname': settings.GROUP_ADDEVENT},
        name='delete_event_permission'),

    # internationalization
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # registration
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/$',
        views.form,
        name='form'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/registered/'
        '(?P<helper_id>[a-z0-9\-]+)/$',
        views.registered,
        name='registered'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/validate/'
        '(?P<helper_id>[a-z0-9\-]+)/$',
        views.validate,
        name='validate'),

    # manage event
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/manage/$',
        views.admin,
        name='manage_event'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/edit/$',
        views.edit_event,
        name='edit_event'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/delete/$',
        views.delete_event,
        name='delete_event'),

    # jobs
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/$',
        views.jobs_and_shifts,
        name='jobs_and_shifts'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/new/$',
        views.edit_job,
        name='new_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/edit/$',
        views.edit_job,
        name='edit_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/delete/$',
        views.delete_job,
        name='delete_job'),

    # shifts
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/shift/'
        '(?P<shift_pk>[0-9]+)/$',
        views.edit_shift,
        name='edit_shift'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/shift/'
        '(?P<shift_pk>[0-9]+)/delete/$',
        views.delete_shift,
        name='delete_shift'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/shift/'
        'new/$',
        views.edit_shift,
        name='new_shift'),

    # helpers
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/$',
        views.helpers,
        name='helpers'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/job/(?P<job_pk>[0-9]+)/$',
        views.helpers,
        name='helpers'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/$',
        views.edit_helper,
        name='edit_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/job/(?P<job_pk>[0-9]+)/$',
        views.edit_helper,
        name='edit_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/delete/(?P<shift_pk>[0-9]+)/$',
        views.delete_helper,
        name='delete_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/delete/(?P<shift_pk>[0-9]+)/all/$',
        views.delete_helper,
        {'show_all_shifts': True},
        name='delete_helper_all'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/delete/coordinator/(?P<job_pk>[0-9]+)/$',
        views.delete_coordinator,
        name='delete_coordinator'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/add/(?P<shift_pk>[0-9]+)/$',
        views.add_helper,
        name='add_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/add/coordinator/'
        '(?P<job_pk>[0-9]+)/$',
        views.add_helper,
        name='add_coordinator'),

    # export
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<type>[a-z]+)/all/$',
        views.export,
        name='export'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<type>[a-z]+)/'
        '(?P<job_pk>[0-9]+)/$',
        views.export,
        name='jobexport'),

    # summaries
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/coordinators/$',
        views.coordinators,
        name='coordinators'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/statistics/$',
        views.statistics,
        name='statistics'),

    # badges
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

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/'
        '(?P<job_pk>[0-9]+)/$',
        views.generate_badges,
        name='generate_badges'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/'
        '(?P<job_pk>[0-9]+)/warnings/$',
        views.badges_warnings,
        name='badges_warnings'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/badges/generate/',
        views.badges,
        name='badges'),

    # manage links
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/links/$',
        views.links,
        name='links'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/links/add/$',
        views.edit_link,
        name='add_link'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/links/(?P<link_pk>[0-9a-f\-]+)/$',
        views.edit_link,
        name='edit_link'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/links/(?P<link_pk>[0-9a-f\-]+)/'
        'delete/$',
        views.delete_link,
        name='delete_link'),

    # use links
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/l/(?P<link_pk>[0-9a-f\-]+)/$',
        views.form,
        name='form_for_link'),

    # send mails
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/mail/$',
        views.mail,
        name='mail'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
