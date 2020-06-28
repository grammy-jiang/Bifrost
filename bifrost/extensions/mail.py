"""
Mail

Refer to:
* https://docs.python.org/3/library/smtplib.html
* https://docs.python.org/3/library/email.message.html

Thanks:
* https://mailtrap.io/
"""
import smtplib
from email.message import EmailMessage
from typing import Any

from bifrost.base import BaseComponent, LoggerMixin
from bifrost.signals import email_sent


class Mail(BaseComponent, LoggerMixin):
    """
    Mail
    """

    name: str = "Mail"
    setting_prefix: str = "MAIL_"

    async def start(self) -> None:
        """

        :return:
        :rtype: None
        """
        self.service.signal_manager.connect(self.send_email, email_sent)
        self.logger.info("Extension [%s] is running...", self.name)

    async def stop(self) -> None:
        """

        :return:
        :rtype: None
        """
        # TODO: remove signal connection
        self.logger.info("Extension [%s] is stopped.", self.name)

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

    def send_email(  # pylint: disable=bad-continuation,unused-argument
        self, sender: Any = None, **kwargs
    ) -> None:
        """

        :param sender:
        :type sender: Any
        :param kwargs:
        :return:
        :rtype: None
        """
        message = self._get_message(**kwargs)

        self.logger.info("Send email [%s] to [%s]", message["Subject"], message["To"])

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
