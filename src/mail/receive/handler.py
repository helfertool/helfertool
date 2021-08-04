from .forwarder import MailForwarder
from .receiver import MailReceiver
from ..tracking import handle_tracking


class DeliveryNotification:
    def __init__(self, recipient, status, error_text, original_mail):
        self.recipient = recipient
        self.status = status
        self.error_text = error_text
        self.original_mail = original_mail

    def __str__(self):
        return "{} - {} - {}".format(self.recipient, self.status, self.error_text)


class MailHandler:
    """
    MailHandler checks a mailbox for new mails, handles the received delivery notifications and forwards
    all other mails.
    """
    def __init__(self):
        self._receiver = MailReceiver()
        self._forwarder = MailForwarder()

    def run(self, do_forward=True):
        """
        Handle new mails and forward unhandled mails to another address.
        """
        self._receiver.connect()
        new_msg_ids = self._receiver.get_message_ids()

        for msg_id in new_msg_ids:
            msg = self._receiver.get_message(msg_id)

            notifications = self._check_delivery_notification(msg)
            msg_handled = False

            if notifications:
                for notification in notifications:
                    # One mail can contain multiple delivery notifications. They are handled separately here,
                    # but the all contain the same original message. If parsing of the original message fails, we can
                    # directly stop.
                    header = self._get_helfertool_header(notification)
                    if header:
                        msg_handled = handle_tracking(header, notification)
                    else:
                        msg_handled = False
                        break  # will be the same for the other delivery notifications

            if not msg_handled and do_forward:
                self._forward(msg)

        self._receiver.close()

    def _check_delivery_notification(self, msg):
        """
        Check if message is a delivery status notification and parse it.

        Returns None or a list of DeliveryNotification objects (one message may contain multiple mail addresses).
        """
        # based on https://stackoverflow.com/questions/5298285/detecting-if-an-email-is-a-delivery-status-notification-and-extract-informatio # noqa

        # it needs to be a multipart message
        if not msg.is_multipart():
            return None

        # get the payload, we need more than one payload
        # we usually should have three payloads:
        #  1) Human readable message
        #  2) Delivery status notification
        #  3) Original mail
        payload = msg.get_payload()

        if len(payload) <= 1:
            return None

        # 3) Original mail
        original_msg = None
        # the original message again is a multipart message...
        if len(payload) >= 3 and payload[2].is_multipart():
            original_msg = payload[2].get_payload()[0]

        # 2) Delivery status notification
        dsn_msg = payload[1]

        if dsn_msg.get_content_type() != 'message/delivery-status':
            return None

        result = []
        for dsn_part in dsn_msg.get_payload():
            if dsn_part.get("action", "") == "failed":
                # recipient address
                if "original-recipient" in dsn_part:
                    recipient = dsn_part.get("original-recipient", "")
                else:
                    recipient = dsn_part.get("final-recipient", "")

                if recipient.startswith("rfc822;"):
                    recipient = recipient[7:].strip()

                # status
                status = dsn_part.get("status", "")

                # error text
                error_text = dsn_part.get("diagnostic-code", "")
                error_text = error_text.split("\n")
                error_text = " ".join([t.strip() for t in error_text])

                # add to results
                notification = DeliveryNotification(recipient, status, error_text, original_msg)
                result.append(notification)

        return result

    def _get_helfertool_header(self, delivery_notification):
        if not delivery_notification.original_mail:
            return None

        return delivery_notification.original_mail.get("X-Helfertool")

    def _forward(self, msg):
        """
        Forward a message to the internal mail address.
        """
        self._forwarder.connect()
        self._forwarder.forward(msg)
        self._forwarder.close()
