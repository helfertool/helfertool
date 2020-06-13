import re
import uuid

MAIL_REGISTRATION = "registration"
MAIL_EVENT = "event"
MAIL_NEWS = "news"

# sonarcloud complains about the following regex, because it contains patterns that are also in queries
# that lead to exponential complexity evaluation.
# the complexity of this regex is linear over the input, so nothing to worry here.
uuid_regex = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')  # NOSONAR


def new_tracking_registration(helper):
    mail_id = "{};{}".format(MAIL_REGISTRATION, helper.pk)
    mail_header = {"X-Helfertool": mail_id}

    return mail_header


def new_tracking_event():
    mail_uuid = uuid.uuid4()
    mail_id = "{};{}".format(MAIL_EVENT, mail_uuid)
    mail_header = {"X-Helfertool": mail_id}

    return mail_uuid, mail_header


def new_tracking_news(person):
    mail_id = "{};{}".format(MAIL_NEWS, person.token)
    mail_header = {"X-Helfertool": mail_id}

    return mail_header


def parse_tracking(value):
    # header format: "type;uuid"
    tmp = value.split(";", 1)
    if len(tmp) != 2:
        raise ValueError("Invalid header format")
    msg_type, uuid_str = tmp

    # check message type
    if msg_type not in (MAIL_EVENT, MAIL_NEWS, MAIL_REGISTRATION):
        raise ValueError("Invalid header type")

    # check uuid
    if uuid_regex.match(uuid_str) is None:
        raise ValueError("Invalid UUID")

    return msg_type, uuid_str
