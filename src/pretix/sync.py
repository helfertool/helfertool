from pretix.models import PretixOrder, PretixItemJobLinkage
from pretix.pretix_client import create_order, cancel_order, change_order


def get_ticket_for_helper(helper):
    if helper.pk is None:
        # helper deleted
        return None
    sorted_jobs = []
    sorted_jobs.extend(helper.coordinated_jobs)
    sorted_jobs.extend((shift.job for shift in sorted(helper.shifts.all(), key=lambda shift: shift.begin)))
    for job in sorted_jobs:
        link = PretixItemJobLinkage.objects.filter(job=job)
        if len(link) > 0:
            return link[0].pretix_item_ref
    return None


def sync_pretix_order(helper, order=None):
    if order is None:
        order = next(iter(PretixOrder.objects.filter(helper=helper)), None)

    item_ref = get_ticket_for_helper(helper)

    if not item_ref and order:
        try:
            if order.pretix_order_id:
                cancel_order(order.pretix_order_id, order.pretix_item_ref)
            order.delete()
            return True
        except:
            return False
    elif order and item_ref != order.pretix_item_ref and order.pretix_order_id:
        try:
            change_order(order.pretix_order_id, order.pretix_order_position_id, order.pretix_item_ref, item_ref)
            order.pretix_item_ref = item_ref
        except:
            order.failed = True
        order.save()
        return not order.failed
    elif item_ref:
        if not order:
            order = PretixOrder(helper=helper, pretix_item_ref=item_ref)
        elif order.pretix_order_id:
            return True
        try:
            (
                order.pretix_order_id,
                order.pretix_order_link,
                order.pretix_order_position_id,
                order.pretix_ticket_code,
            ) = create_order(item_ref, helper)
        except:
            order.failed = True
        order.save()
        return not order.failed
    return True
