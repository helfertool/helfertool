def warnings_for_job(job):
    result = []

    for helper in job.helpers_and_coordinators():
        if helper.badge.is_ambiguous() \
            and (helper.is_coordinator
                 or not job.event.badge_settings.only_coordinators):
            result.append(helper)

    return result
