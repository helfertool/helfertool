from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views
from .feeds import HelperFeed

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # about
    url(r'^about/$',
        TemplateView.as_view(template_name='registration/about.html'),
        name='about'),

    # account
    url(r'^account/$',
        views.change_user,
        name='change_user'),

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

    url(r'^admin/permissions/(?P<user_pk>[0-9]+)/news/delete/$',
        views.delete_permission, {'groupname': settings.GROUP_SENDNEWS},
        name='delete_news_permission'),

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

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/ical/'
        '(?P<helper_id>[a-z0-9\-]+)/$',
        HelperFeed(),
        name='ical'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/update/'
        '(?P<helper_id>[a-z0-9\-]+)/$',
        views.update_personal,
        name='update_personal'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/deregister/'
        '(?P<helper_id>[a-z0-9\-]+)/(?P<shift_pk>[0-9]+)/$',
        views.deregister,
        name='deregister'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/deleted/',
        views.deleted,
        name='deleted'),

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

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/archive/$',
        views.archive_event,
        name='archive_event'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/duplicate/$',
        views.duplicate_event,
        name='duplicate_event'),

    # jobs
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/$',
        views.jobs_and_shifts,
        name='jobs_and_shifts'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/new/$',
        views.edit_job,
        name='new_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/sort/$',
        views.sort_job,
        name='sort_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/edit/$',
        views.edit_job,
        name='edit_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/delete/$',
        views.delete_job,
        name='delete_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/jobs/(?P<job_pk>[0-9]+)/'
        'duplicate/$',
        views.duplicate_job,
        name='duplicate_job'),

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

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/search/$',
        views.search_helper,
        name='search_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/$',
        views.view_helper,
        name='view_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/edit/$',
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

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/add/'
        '(?P<shift_pk>[0-9]+)/$',
        views.add_helper,
        name='add_helper'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/add/coordinator/'
        '(?P<job_pk>[0-9]+)/$',
        views.add_coordinator,
        name='add_coordinator'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/add/shift/$',
        views.add_helper_to_shift,
        name='add_helper_to_shift'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/add/coordinator/$',
        views.add_helper_as_coordinator,
        name='add_helper_as_coordinator'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/helpers/'
        '(?P<helper_pk>[0-9a-f\-]+)/resend/$',
        views.resend_mail,
        name='resend_mail'),

    # export
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/all/$',
        views.export,
        name='export'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/all/'
        '(?P<date_str>\d{4}-\d{2}-\d{2})/$',
        views.export,
        name='export_date'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/'
        '(?P<job_pk>[0-9]+)/$',
        views.export,
        name='export_job'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/export/(?P<filetype>[a-z]+)/'
        '(?P<job_pk>[0-9]+)/(?P<date_str>\d{4}-\d{2}-\d{2})/$',
        views.export,
        name='export_job_date'),

    # summaries
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/coordinators/$',
        views.coordinators,
        name='coordinators'),

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

    # duplicates
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/duplicates/$',
        views.duplicates,
        name='duplicates'),

    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/duplicates/merge/(?P<email>.+)/$',
        views.merge,
        name='merge'),

    # use links
    url(r'^(?P<event_url_name>[a-zA-Z0-9]+)/l/(?P<link_pk>[0-9a-f\-]+)/$',
        views.form,
        name='form_for_link'),
]
