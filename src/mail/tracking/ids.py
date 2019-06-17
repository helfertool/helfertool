import uuid

MAIL_REGISTRATION = "registration"
MAIL_EVENT = "event"
MAIL_NEWS = "news"


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
