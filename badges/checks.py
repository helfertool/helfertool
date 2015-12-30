def warnings_for_job(job):
    result = []

    for helper in job.helpers_and_coordinators():
        if helper.badge.is_ambiguous():
            result.append(helper)

    return result
