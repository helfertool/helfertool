from .models import Prerequisite


def prerequisites_for_helper(helper):
    return Prerequisite.objects.filter(job__shift__helper=helper).distinct()
