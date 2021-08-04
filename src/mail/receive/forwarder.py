from django.conf import settings

from .error import MailHandlerError

import email
import smtplib


class MailForwarder:
    """
    MailForwarder sends an existing mail again to the internal address (forward_unhandled_address) over SMTP.

    It rewrites the mail to be conform to DMARC, otherwise the mail could be dropped by the receiving mail server.
    This is used by MailHandler.
    """
    def __init__(self):
        self._connection = None

        self._own_addresses = [settings.EMAIL_SENDER_ADDRESS.lower(), ]
        if settings.FORWARD_UNHANDLED_ADDRESS:
            self._own_addresses.append(settings.FORWARD_UNHANDLED_ADDRESS.lower())

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

        # get original From name and address -> there is only one From address allowed
        froms = self._cleaned_getaddresses(msg, 'from', keep_own=True)
        if len(froms) > 0:
            original_from_name, original_from_address = froms[0]
        else:
            original_from_name = original_from_address = None

        # get original TO, CC and Reply-To names and addresses
        # both own addresses are removed from the lists, so only external addresses are in there
        original_to = self._cleaned_getaddresses(msg, 'to')
        original_cc = self._cleaned_getaddresses(msg, 'cc')
        original_reply_to = self._cleaned_getaddresses(msg, 'reply-to')

        # Change From: ... via ... <...@...>
        new_from_name = original_from_name or original_from_address or "Unknown"
        new_from_name_suffix = " via {}".format(settings.FORWARD_UNHANDLED_NAME)
        if new_from_name.endswith(new_from_name_suffix):
            # "via ..." suffix already there -> do not add it again
            new_from = new_from_name
        else:
            new_from = new_from_name + new_from_name_suffix

        self._replace_header(msg, "From", email.utils.formataddr((new_from, settings.FORWARD_UNHANDLED_ADDRESS)))

        # Change To: internal forwarding address + original to (without own addresses)
        new_to = [(settings.FORWARD_UNHANDLED_NAME, settings.FORWARD_UNHANDLED_ADDRESS)]
        self._merge_addr_list(new_to, original_to)
        self._replace_header(msg, "To", self._format_addr_header(new_to))

        # CC is not touched (it is only informational)

        # Change Reply-To: public address + original reply-to + original from + original to + original CC
        # the own addresses are already filtered out of the original headers, so only the public address is added here
        new_reply_to = [(settings.EMAIL_SENDER_NAME, settings.EMAIL_SENDER_ADDRESS), ]
        self._merge_addr_list(new_reply_to, original_reply_to)
        self._merge_addr(new_reply_to, original_from_name, original_from_address)
        self._merge_addr_list(new_reply_to, original_to)
        self._merge_addr_list(new_reply_to, original_cc)

        self._replace_header(msg, "reply-to", self._format_addr_header(new_reply_to))

        # send mail
        self._connection.sendmail(settings.FORWARD_UNHANDLED_ADDRESS, settings.FORWARD_UNHANDLED_ADDRESS,
                                  msg.as_string())

    def _cleaned_getaddresses(self, msg, header, keep_own=False):
        addresses = email.utils.getaddresses(msg.get_all(header, []))

        valid_addresses = []
        for addr in addresses:
            # addr is tuple of name and address

            # remove invalid things
            if '@' not in addr[1]:
                continue

            # remove own addresses
            if keep_own is False and addr[1].lower() in self._own_addresses:
                continue

            # otherwise: add
            valid_addresses.append(addr)

        return valid_addresses

    def _merge_addr(self, addresses, new_name, new_mail):
        # new name and mail None -> abort
        if not new_name and not new_mail:
            return

        # new name None -> use mail
        if not new_name:
            new_name = new_mail

        # already in there -> abort
        for _, mail in addresses:
            if mail.lower() == new_mail.lower():
                return

        # add
        addresses.append((new_name, new_mail))

    def _merge_addr_list(self, addresses, new_addresses):
        for new_name, new_mail in new_addresses:
            self._merge_addr(addresses, new_name, new_mail)

    def _format_addr_header(self, addresses):
        return ", ".join([email.utils.formataddr(addr) for addr in addresses])

    def _replace_header(self, msg, key, value):
        if key in msg:
            msg.replace_header(key, value)
        else:
            msg.add_header(key, value)
