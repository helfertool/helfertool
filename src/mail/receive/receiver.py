from django.conf import settings

from .error import MailHandlerError

import email
import imaplib
import socket

# look at the calendar, it's not 19xx anymore
imaplib._MAXLINE = 1000000


class MailReceiver:
    """
    MailReceiver checks an IMAP mailbox for new mails.

    It checks one particular folder and returns the unseen messages. This is used by MailHandler.
    """

    def __init__(self):
        self._connection = None

    def connect(self):
        """
        Connect to IMAP server and select given folder.
        """
        if self._connection:
            raise MailHandlerError("IMAP connection already opened")

        # connect
        try:
            if settings.RECEIVE_EMAIL_USE_SSL:
                self._connection = imaplib.IMAP4_SSL(host=settings.RECEIVE_EMAIL_HOST, port=settings.RECEIVE_EMAIL_PORT)
            else:
                self._connection = imaplib.IMAP4(host=settings.RECEIVE_EMAIL_HOST, port=settings.RECEIVE_EMAIL_PORT)

            if settings.RECEIVE_EMAIL_USE_TLS:
                self._connection.starttls()
        except (imaplib.IMAP4.error, ConnectionRefusedError, socket.gaierror):
            raise MailHandlerError("Invalid hostname, port or TLS settings for IMAP")

        # login
        try:
            self._connection.login(settings.RECEIVE_EMAIL_HOST_USER, settings.RECEIVE_EMAIL_HOST_PASSWORD)
        except imaplib.IMAP4.error:
            raise MailHandlerError("Invalid username or password for IMAP")

        # select folder
        try:
            ret, data = self._connection.select(settings.RECEIVE_EMAIL_FOLDER)

            if ret != "OK":
                raise MailHandlerError("Invalid folder")
        except imaplib.IMAP4.error:
            raise MailHandlerError("Invalid folder")

    def close(self):
        """
        Close IMAP connection.
        """
        if self._connection:
            self._connection.close()
            self._connection.logout()
            self._connection = None

    def get_message_ids(self):
        """
        Returns message IDs of unseen messages
        """
        ret, data = self._connection.search(None, "UNSEEN")
        if ret != "OK":
            raise RuntimeError(data)

        return data[0].strip().decode().split()

    def get_message(self, msg_id):
        """
        Fetch one message from server. This marks the message as seen.
        """
        _, data = self._connection.fetch(msg_id, "(RFC822)")

        if not data:
            return None

        try:
            return email.message_from_bytes(data[0][1])
        except TypeError:
            # Something happened to the message in parallel, ignore it
            return None
