from django.urls import path

from . import views

app_name = "badges"
urlpatterns = [
    #
    # settings
    #
    path("<slug:event_url_name>/badges/settings/", views.settings, name="settings"),
    path("<slug:event_url_name>/badges/settings/advanced/", views.settings_advanced, name="settings_advanced"),
    path("<slug:event_url_name>/badges/defaulttemplate/", views.default_template, name="default_template"),
    path("<slug:event_url_name>/badges/currenttemplate/", views.current_template, name="current_template"),
    #
    # edit badge
    #
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/badge/",
        views.edit_badge,
        name="edit_badge",
    ),
    path(
        "<slug:event_url_name>/helpers/<uuid:helper_pk>/badge/photo/",
        views.get_badge_photo,
        name="get_badge_photo",
    ),
    #
    # permission
    #
    path(
        "<slug:event_url_name>/badges/permission/<int:permission_pk>/",
        views.edit_permission,
        name="edit_permission",
    ),
    path("<slug:event_url_name>/badges/permission/add/", views.edit_permission, name="new_permission"),
    path(
        "<slug:event_url_name>/badges/permission/<int:permission_pk>/delete/",
        views.delete_permission,
        name="delete_permission",
    ),
    #
    # role
    #
    path("<slug:event_url_name>/badges/role/<int:role_pk>/", views.edit_role, name="edit_role"),
    path("<slug:event_url_name>/badges/role/add/", views.edit_role, name="new_role"),
    path(
        "<slug:event_url_name>/badges/role/<int:role_pk>/delete/",
        views.delete_role,
        name="delete_role",
    ),
    #
    # design
    #
    path(
        "<slug:event_url_name>/badges/design/<int:design_pk>/",
        views.edit_design,
        name="edit_design",
    ),
    path("<slug:event_url_name>/badges/design/add/", views.edit_design, name="new_design"),
    path(
        "<slug:event_url_name>/badges/design/<int:design_pk>/delete/",
        views.delete_design,
        name="delete_design",
    ),
    path(
        "<slug:event_url_name>/badges/design/<int:design_pk>/bg/<side>/",
        views.get_design_bg,
        name="get_design_bg",
    ),
    #
    # badge generation
    #
    # overview page
    path("<slug:event_url_name>/badges/", views.index, name="index"),
    # overview of generated badges (list of tasks)
    path("<slug:event_url_name>/badges/tasklist/", views.tasklist, name="tasklist"),
    # warnings
    path("<slug:event_url_name>/badges/warnings/<int:job_pk>/", views.warnings, name="warnings"),
    # generate for job
    path(
        "<slug:event_url_name>/badges/generate/<int:job_pk>/",
        views.generate,
        {"generate": "job"},
        name="generate_for_job",
    ),
    path(
        "<slug:event_url_name>/badges/generate/<int:job_pk>/all/",
        views.generate,
        {"generate": "job", "skip_printed": False},
        name="generate_all_for_job",
    ),
    # generate special badges
    path(
        "<slug:event_url_name>/badges/generate/special/",
        views.generate,
        {"generate": "special"},
        name="generate_special",
    ),
    path(
        "<slug:event_url_name>/badges/generate/special/all/",
        views.generate,
        {"generate": "special", "skip_printed": False},
        name="generate_all_special",
    ),
    # generate for all jobs and special badges
    path("<slug:event_url_name>/badges/generate/", views.generate, {"generate": "all"}, name="generate"),
    path(
        "<slug:event_url_name>/badges/generate/all/",
        views.generate,
        {"generate": "all", "skip_printed": False},
        name="generate_all",
    ),
    # failed page
    path("<slug:event_url_name>/badges/failed/<task_id>/", views.failed, name="failed"),
    # download badges
    path(
        "<slug:event_url_name>/badges/download/<task_id>/",
        views.download,
        name="download",
    ),
    #
    # register badges
    #
    path("<slug:event_url_name>/badges/register/", views.register, name="register"),
    #
    # special badges
    #
    path("<slug:event_url_name>/badges/special/", views.list_specialbadges, name="list_specialbadges"),
    path(
        "<slug:event_url_name>/badges/special/<int:specialbadges_pk>/",
        views.edit_specialbadges,
        name="edit_specialbadges",
    ),
    path("<slug:event_url_name>/badges/special/add/", views.edit_specialbadges, name="new_specialbadges"),
    path(
        "<slug:event_url_name>/badges/special/<int:specialbadges_pk>/template/",
        views.edit_specialbadges_template,
        name="edit_specialbadges_template",
    ),
    path(
        "<slug:event_url_name>/badges/special/<int:specialbadges_pk>/delete/",
        views.delete_specialbadges,
        name="delete_specialbadges",
    ),
    path(
        "<slug:event_url_name>/badges/special/<int:specialbadges_pk>/template/photo/",
        views.get_specialbadges_photo,
        name="get_specialbadges_photo",
    ),
]
