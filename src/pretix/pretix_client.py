import json
from collections import namedtuple
from urllib.error import HTTPError

from django.conf import settings
from urllib.request import Request, urlopen
from urllib.parse import urljoin

PretixItem = namedtuple("PretixItem", ("ref", "org_name", "event_name", "item_name"))

ITEM_REF_PART_SEPERATOR = ","


def call_api(pretix_system, path, json_body=None):
    data = json.dumps(json_body).encode("utf-8") if json_body else None
    request = Request(
        url=urljoin(pretix_system["url"], path),
        data=data,
        headers={"Authorization": f"Token {pretix_system['token']}", "Content-Type": "application/json"},
    )
    print(json_body)
    print(path)
    try:
        response = urlopen(request)
    except HTTPError as e:
        response = e
    response_body = json.load(response)
    print(response_body)
    return response_body


def enumerate_items(event):
    pretix_systems = [
        system
        for system in settings.PRETIX_SYSTEMS
        if system["allowed_events"] is None or event.url_name in system["allowed_events"]
    ]

    all_items = []
    errors = []

    for pretix_system in pretix_systems:

        try:
            organisations = call_api(pretix_system, "/api/v1/organizers/")["results"]
        except:
            errors.append(f"organisations of '{pretix_system['name']}'")
            continue
        for organisation in organisations:
            try:
                events = call_api(pretix_system, f"/api/v1/organizers/{organisation['slug']}/events/")["results"]
            except:
                errors.append([f"events of organisation '{organisation.get('slug')}'"])
                continue
            for event in events:
                try:
                    items = call_api(
                        pretix_system, f"/api/v1/organizers/{organisation['slug']}/events/{event['slug']}/items/"
                    )["results"]
                except:
                    errors.append([f"items of event '{event.get('slug')}'"])
                    continue
                for item in items:
                    try:
                        all_items.append(
                            PretixItem(
                                ref=f"{pretix_system['name']}{ITEM_REF_PART_SEPERATOR}{organisation['slug']}{ITEM_REF_PART_SEPERATOR}{event['slug']}{ITEM_REF_PART_SEPERATOR}{item['id']}",
                                org_name=organisation["name"],
                                event_name=next(iter(event["name"].values())),
                                item_name=next(iter(item["name"].values())),
                            )
                        )
                    except:
                        errors.append([f"item '{item.get('id')}'"])

    return all_items, errors


def get_pretix_system(pretix_system_name):
    pretix_system = next((system for system in settings.PRETIX_SYSTEMS if system["name"] == pretix_system_name), None)
    if not pretix_system:
        raise Exception("Pretix system not found")
    return pretix_system


def create_order(item_ref, helper):
    pretix_system_name, org_slug, event_slug, item_id = item_ref.split(ITEM_REF_PART_SEPERATOR)
    pretix_system = next((system for system in settings.PRETIX_SYSTEMS if system["name"] == pretix_system_name), None)
    if not pretix_system:
        raise Exception(f"Pretix system not {pretix_system_name} found")
    request = {
        "locale": "en",
        "email": helper.email,
        "payment_provider": "free",
        "positions": [
            {
                "item": int(item_id),
                "price": "0.00",
                "attendee_email": helper.email,
                "attendee_name": f"{helper.firstname} {helper.surname}",
            }
        ],
        "fees": [],
    }
    result = call_api(pretix_system, f"/api/v1/organizers/{org_slug}/events/{event_slug}/orders/", request)
    order_position = result["positions"][0]
    return result["code"], result["url"], order_position["id"], order_position["secret"]


def cancel_order(order_id, item_ref):
    pretix_system_name, org_slug, event_slug, item_id = item_ref.split(ITEM_REF_PART_SEPERATOR)
    pretix_system = get_pretix_system(pretix_system_name)
    request = {
        "state": "done",
        "source": "admin",
        "amount": "0.00",
        "provider": "free",
        "mark_canceled": True,
        "mark_pending": False,
    }
    print(
        call_api(
            pretix_system, f"/api/v1/organizers/{org_slug}/events/{event_slug}/orders/{order_id}/refunds/", request
        )
    )


def change_order(order_id, order_position_id, old_item_ref, new_item_ref):
    old_pretix_system_name, old_org_slug, old_event_slug, old_item_id = old_item_ref.split(ITEM_REF_PART_SEPERATOR)
    new_pretix_system_name, new_org_slug, new_event_slug, new_item_id = new_item_ref.split(ITEM_REF_PART_SEPERATOR)
    if (
        old_pretix_system_name != new_pretix_system_name
        or old_org_slug != new_org_slug
        or old_event_slug != new_event_slug
    ):
        raise Exception("Could not change order to different event")
    pretix_system = get_pretix_system(new_pretix_system_name)
    request = {
        "patch_positions": [
            {
                "position": order_position_id,
                "body": {
                    "item": int(new_item_id),
                    "price": "0.00",
                },
            }
        ]
    }
    print(
        call_api(
            pretix_system,
            f"/api/v1/organizers/{new_org_slug}/events/{new_event_slug}/orders/{order_id}/change/",
            request,
        )
    )
