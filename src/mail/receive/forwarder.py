from django.conf import settings

import email
import smtplib

from .error import MailHandlerError


class MailForwarder:
    """
    MailForwarder sends an existing mail again to the internal address (forward_unhandled_address) over SMTP.

    It rewrites the mail to be conform to DMARC, otherwise the mail could be dropped by the receiving mail server.
    This is used by MailHandler.
    """
    def __init__(self):
        self._connection = None

    def connect(self):
        """
        Connect to SMTP server.
        """
        if self._connection:
            raise MailHandlerError("SMTP connection already opened")

        try:
            if settings.EMAIL_USE_SSL:
                self._connection = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                self._connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)

            if settings.EMAIL_USE_TLS:
                self._connection.starttls()
        except smtplib.SMTPException:
            raise MailHandlerError("Invalid hostname, port or TLS settings for SMTP")

        try:
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                self._connection.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        except smtplib.SMTPException:
            raise MailHandlerError("Invalid username or password for SMTP")

    def close(self):
        """
        Close connection to SMTP server.
        """
        if self._connection:
            self._connection.quit()
            self._connection = None

    def forward(self, msg):
        # headers that should be deleted, collected from mailman handlers:
        # https://gitlab.com/mailman/mailman/blob/master/src/mailman/handlers/
        headers_to_delete = (
            "approve",
            "approved",
            "archived-at",
            "authentication-results",
            "disposition-notification-to",
            "dkim-signature",
            "domainkey-signature",
            "errors-to",
            "resent-bcc",
            "resent-cc",
            "resent-date",
            "resent-from",
            "resent-message-id",
            "resent-to",
            "return-path",
            "return-receipt-to",
            "sender",
            "urgent",
            "x-approve",
            "x-approved",
            "x-confirm-reading-to",
            "x-google-dkim-signature",
            "x-pmrqc",
        )

        for h in headers_to_delete:
            del msg[h]

        # rewrite headers (source: https://gitlab.com/mailman/mailman/blob/master/src/mailman/handlers/dmarc.py)

        # get from name and address
        all_froms = email.utils.getaddresses(msg.get_all('from', []))
        froms = [email for email in all_froms if '@' in email[1]]  # remove invalid things
        if len(froms) > 0:
            original_from_name, original_from_address = froms[0]
        else:
            original_from_name = original_from_address = None

        # To: internal address
        to = (settings.FORWARD_UNHANDLED_NAME, settings.FORWARD_UNHANDLED_ADDRESS)
        msg.replace_header("To", email.utils.formataddr(to))

        # From: ... via ... <...@...>
        new_from_name = original_from_name or original_from_address
        new_from_name_suffix = " via {}".format(settings.FORWARD_UNHANDLED_NAME)
        if new_from_name.endswith(new_from_name_suffix):
            # "via ..." suffix already there -> do not add it again
            new_from = new_from_name
        else:
            new_from = new_from_name + new_from_name_suffix

        msg.replace_header("From", email.utils.formataddr((new_from, settings.FORWARD_UNHANDLED_ADDRESS)))

        # Reply-to: original reply-to + original from + public address
        reply_to = email.utils.getaddresses(msg.get_all("reply-to", []))
        reply_to_addresses = [a[1] for a in reply_to]

        if settings.EMAIL_SENDER_ADDRESS not in reply_to_addresses:
            reply_to.append((settings.EMAIL_SENDER_NAME, settings.EMAIL_SENDER_ADDRESS))
            reply_to_addresses.append(settings.EMAIL_SENDER_ADDRESS)

        if original_from_address not in reply_to_addresses:
            reply_to.append((original_from_name, original_from_address))
            reply_to_addresses.append(original_from_address)

        if "reply-to" in msg:
            msg.replace_header("reply-to", ", ".join([email.utils.formataddr(a) for a in reply_to]))
        else:
            msg.add_header("reply-to", ", ".join([email.utils.formataddr(a) for a in reply_to]))

        # send mail
        self._connection.sendmail(settings.FORWARD_UNHANDLED_ADDRESS, settings.FORWARD_UNHANDLED_ADDRESS, msg.as_string())
