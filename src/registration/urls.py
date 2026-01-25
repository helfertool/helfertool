from django.urls import path
from django.views.generic import TemplateView

from . import views
from .feeds import HelperFeed

urlpatterns = [
    path("", views.index, name="index"),
    path("all/", views.index_all_events, name="index_all_events"),
    # about
    path("about/", TemplateView.as_view(template_name="registration/about.html"), name="about"),
    # admin interface
    path("manage/", views.admin, name="admin"),
    path("manage/new/", views.edit_event, name="new_event"),
    # registration
    path("<slug:event_url_name>/", views.form, name="form"),
    path(
        "<slug:event_url_name>/registered/<uuid:helper_pk>/",
        views.registered,
        name="registered",
    ),
    path(
        "<slug:event_url_name>/validate/<uuid:helper_pk>/<uuid:validation_id>/",
        views.validate,
        name="validate",
    ),
    path("<slug:event_url_name>/ical/<uuid:helper_pk>/", HelperFeed(), name="ical"),
    path(
        "<slug:event_url_name>/update/<uuid:helper_pk>/",
        views.update_personal,
        name="update_personal",
    ),
    path(
        "<slug:event_url_name>/deregister/<uuid:helper_pk>/<int:shift_pk>/",
        views.deregister,
        name="deregister",
    ),
    path("<slug:event_url_name>/deleted/", views.deleted, name="deleted"),
    # manage event
    path("<slug:event_url_name>/edit/", views.edit_event, name="edit_event"),
    path("<slug:event_url_name>/admins/", views.edit_event_admins, name="edit_event_admins"),
    path("<slug:event_url_name>/delete/", views.delete_event, name="delete_event"),
    path("<slug:event_url_name>/archive/", views.archive_event, name="archive_event"),
    path("<slug:event_url_name>/duplicate/", views.duplicate_event, name="duplicate_event"),
    path("<slug:event_url_name>/move/", views.move_event, name="move_event"),
    path("<slug:event_url_name>/logo/<logotype>/", views.get_event_logo, name="get_event_logo"),
    # jobs
    path("<slug:event_url_name>/jobs/", views.jobs_and_shifts, name="jobs_and_shifts"),
    path("<slug:event_url_name>/jobs/new/", views.edit_job, name="new_job"),
    path("<slug:event_url_name>/jobs/sort/", views.sort_job, name="sort_job"),
    path("<slug:event_url_name>/jobs/<int:job_pk>/edit/", views.edit_job, name="edit_job"),
    path(
        "<slug:event_url_name>/jobs/<int:job_pk>/admins/",
        views.edit_job_admins,
        name="edit_job_admins",
    ),
    path("<slug:event_url_name>/jobs/<int:job_pk>/delete/", views.delete_job, name="delete_job"),
    path(
        "<slug:event_url_name>/jobs/<int:job_pk>/duplicate/",
        views.duplicate_job,
        name="duplicate_job",
    ),
    path(
        "<slug:event_url_name>/jobs/<int:job_pk>/duplicate/day/",
        views.duplicate_job_day,
        name="duplicate_job_day",
    ),
    # shifts
    path(
        "<slug:event_url_name>/jobs/<int:job_pk>/shift/<int:shift_pk>/",
        views.edit_shift,
        name="edit_shift",
    ),
    path(
        "<slug:event_url_name>/jobs/<int:job_pk>/shift/<int:shift_pk>/delete/",
        views.delete_shift,
        name="delete_shift",
    ),
    path("<slug:event_url_name>/jobs/<int:job_pk>/shift/new/", views.edit_shift, name="new_shift"),
    # helpers
    path("<slug:event_url_name>/helpers/", views.helpers, name="helpers"),
    path(
        "<slug:event_url_name>/helpers/job/<int:job_pk>/",
        views.helpers_for_job,
        name="helpers_for_job",
    ),
    path("<slug:event_url_name>/helpers/search/", views.search_helper, name="search_helper"),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/",
        views.view_helper,
        name="view_helper",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/edit/",
        views.edit_helper,
        name="edit_helper",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/delete/<int:shift_pk>/",
        views.delete_helper,
        name="delete_helper",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/delete/<int:shift_pk>/all/",
        views.delete_helper,
        {"show_all_shifts": True},
        name="delete_helper_all",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/delete/coordinator/<int:job_pk>/",
        views.delete_coordinator,
        name="delete_coordinator",
    ),
    path("<slug:event_url_name>/helpers/add/<int:shift_pk>/", views.add_helper, name="add_helper"),
    path(
        "<slug:event_url_name>/helpers/add/coordinator/<int:job_pk>/",
        views.add_coordinator,
        name="add_coordinator",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/add/shift/",
        views.add_helper_to_shift,
        name="add_helper_to_shift",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/add/coordinator/",
        views.add_helper_as_coordinator,
        name="add_helper_as_coordinator",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/resend/",
        views.resend_mail,
        name="resend_mail",
    ),
    # export
    path("<slug:event_url_name>/export/<filetype>/all/", views.export, name="export"),
    path(
        "<slug:event_url_name>/export/<filetype>/all/<date:date>/",
        views.export,
        name="export_date",
    ),
    path(
        "<slug:event_url_name>/export/<filetype>/<int:job_pk>/",
        views.export,
        name="export_job",
    ),
    path(
        "<slug:event_url_name>/export/<filetype>/<int:job_pk>/<date:date>/",
        views.export,
        name="export_job_date",
    ),
    # vacant shifts
    path("<slug:event_url_name>/vacant/", views.vacant_shifts, name="vacant_shifts"),
    # summaries
    path("<slug:event_url_name>/coordinators/", views.coordinators, name="coordinators"),
    # manage links
    path("<slug:event_url_name>/links/", views.links, name="links"),
    path("<slug:event_url_name>/links/add/", views.edit_link, name="add_link"),
    path("<slug:event_url_name>/links/<uuid:link_pk>/", views.edit_link, name="edit_link"),
    path(
        "<slug:event_url_name>/links/<uuid:link_pk>/delete/",
        views.delete_link,
        name="delete_link",
    ),
    # duplicates
    path("<slug:event_url_name>/duplicates/", views.duplicates, name="duplicates"),
    path("<slug:event_url_name>/duplicates/merge/<email>/", views.merge, name="merge"),
    # use links
    path("<slug:event_url_name>/l/<uuid:link_pk>/", views.form, name="form_for_link"),
]
