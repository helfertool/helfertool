def warnings_for_job(job):
    result = []

    for h in job.helpers_and_coordinators():
        if h.badge.is_ambiguous():
            result.append(h)

    return result
