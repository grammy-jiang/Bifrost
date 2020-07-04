"""
Channel
"""
import ssl
from typing import Optional

from bifrost.base import BaseComponent, LoggerMixin
from bifrost.utils.loop import get_event_loop
from bifrost.utils.misc import load_object


class Channel(BaseComponent, LoggerMixin):
    """
    Channel
    """

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service: Service
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        super(Channel, self).__init__(service, name, setting_prefix)

        self.config.update(self.settings["CHANNELS"][self.name])

        self.server = None

    @property
    def signal_manager(self):
        """

        :return:
        :rtype:
        """
        return self.service.signal_manager

    @property
    def stats(self):
        """

        :return:
        :rtype:
        """
        return self.service.stats

    async def start(self) -> None:
        """

        :return:
        :rtype: None
        """
        cls_interface = load_object(self.config["INTERFACE_PROTOCOL"])

        loop = get_event_loop(self.settings)

        ssl_context: Optional[ssl.SSLContext]
        if self.config.get("INTERFACE_SSL_CERT_FILE"):
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(
                certfile=self.config.get("INTERFACE_SSL_CERT_FILE"),
                keyfile=self.config.get("INTERFACE_SSL_KEY_FILE"),
                password=self.config.get("INTERFACE_SSL_PASSWORD"),
            )
        else:
            ssl_context = None

        self.server = await loop.create_server(
            protocol_factory=lambda: cls_interface.from_channel(self),
            host=self.config["INTERFACE_ADDRESS"],
            port=self.config["INTERFACE_PORT"],
            ssl=ssl_context,
        )

        self.logger.info(
            "Channel [%s] is open; "
            "Protocol [%s] is listening on the interface: [%s:%s]",
            self.name,
            self.config["INTERFACE_PROTOCOL"],
            self.config["INTERFACE_ADDRESS"],
            self.config["INTERFACE_PORT"],
        )

    async def stop(self) -> None:
        """

        :return:
        :rtype: None
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("Channel [%s] is closed.", self.name)
