import registration
import mail

from .ids import parse_tracking, MAIL_EVENT, MAIL_NEWS, MAIL_REGISTRATION

import logging
logger = logging.getLogger("helfertool.mail")


def _handle_event(uuid_str, deliverynotification):
    # uuid if tracking_uuid of SentMail
    try:
        sentmail = mail.models.SentMail.objects.get(tracking_uuid=uuid_str)
    except (mail.models.SentMail.DoesNotExist, mail.models.SentMail.MultipleObjectsReturned):
        return False

    # now find the MailDelivery based on the mail address
    maildeliveries = mail.models.MailDelivery.objects.filter(sentmail=sentmail,
                                                             helper__email=deliverynotification.recipient)
    if not maildeliveries.exists():
        return False

    for delivery in maildeliveries:
        delivery.failed = deliverynotification.error_text
        delivery.save()

        logger.info("mail handled", extra={
            'type': MAIL_EVENT,
            'event': delivery.helper.event,
            'helper': delivery.helper,
            'mail_tracking': sentmail.tracking_uuid,
        })

    return True


def _handle_registration(uuid_str, deliverynotification):
    # uuid is PK of helper
    try:
        helper = registration.models.Helper.objects.get(id=uuid_str)
        helper.mail_failed = deliverynotification.error_text
        helper.save()

        logger.info("mail handled", extra={
            'type': MAIL_REGISTRATION,
            'event': helper.event,
            'helper': helper,
        })

        return True
    except registration.models.Helper.DoesNotExist:
        return False


_handlers = {
    MAIL_EVENT: _handle_event,
    MAIL_NEWS: None,
    MAIL_REGISTRATION: _handle_registration,
}


def handle_tracking(header_value, deliverynotification):
    # parse header
    try:
        msg_type, uuid_str = parse_tracking(header_value)
    except ValueError:
        return False

    # call handler
    handler = _handlers.get(msg_type, None)
    if handler:
        return handler(uuid_str, deliverynotification)
    return False
