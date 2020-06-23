"""
Mail

Refer to:
* https://docs.python.org/3/library/smtplib.html
* https://docs.python.org/3/library/email.message.html

Thanks:
* https://mailtrap.io/
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import TYPE_CHECKING, Any

from bifrost.extensions import BaseExtension
from bifrost.signals import email_sent

if TYPE_CHECKING:
    from bifrost.service import Service

logger = logging.getLogger(__name__)


class Mail(BaseExtension):
    """
    Mail
    """

    name = "Mail"
    setting_prefix = "MAIL_"

    @classmethod
    def from_service(cls, service: Service) -> Mail:
        """

        :param service:
        :type service: Service
        :return:
        :rtype: Mail
        """
        obj = super(Mail, cls).from_service(service)

        service.signal_manager.connect(obj.send, email_sent)

        return obj

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        super(Mail, self).service_started(sender)
        logger.info("Extension [%s] is running...", self.name)

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is stopped.", self.name)

    def _get_message(self, **kwargs) -> EmailMessage:
        """

        :param kwargs:
        :return:
        ;:rtype: EmailMessage
        """
        message = EmailMessage()

        message["From"] = kwargs["from"] if "from" in kwargs else self.config["FROM"]
        message["To"] = kwargs["to"] if "to" in kwargs else self.config["TO"]
        message["Subject"] = (
            kwargs["subject"] if "subject" in kwargs else self.config["SUBJECT"]
        )
        message.set_content(
            kwargs["content"] if "content" in kwargs else self.config["CONTENT"]
        )

        return message

    def send(self, sender: Any = None, **kwargs) -> None:
        """

        :param sender:
        :type sender: Any
        :param kwargs:
        :return:
        :rtype: None
        """
        message = self._get_message(**kwargs)

        logger.info("Send email [%s] to [%s]", message["Subject"], message["To"])

        server = kwargs["server"] if "server" in kwargs else self.config["SERVER"]
        port = kwargs["port"] if "port" in kwargs else self.config["PORT"]
        username = (
            kwargs["username"] if "username" in kwargs else self.config["username"]
        )
        password = (
            kwargs["password"] if "password" in kwargs else self.config["PASSWORD"]
        )

        with smtplib.SMTP(server, port) as email_server:
            email_server.login(user=username, password=password)
            email_server.send_message(message)
