"""
Channel
"""
from __future__ import annotations

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

        self.interface_protocol: str = self.config["INTERFACE_PROTOCOL"]
        self.cls_interface_protocol = load_object(self.interface_protocol)
        self.interface_address: str = self.config["INTERFACE_ADDRESS"]
        self.interface_port: int = self.config["INTERFACE_PORT"]

        self.client_protocol: str = self.config["CLIENT_PROTOCOL"]
        self.cls_client_protocol = load_object(self.client_protocol)
        self.client_protocol_address: Optional[str] = self.config.get(
            "CLIENT_PROTOCOL_ADDRESS"
        )
        self.client_protocol_port: Optional[int] = self.config.get(
            "CLIENT_PROTOCOL_PORT"
        )

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
        loop = get_event_loop(self.settings)
        self.server = await loop.create_server(
            lambda: self.cls_interface_protocol.from_channel(self),
            self.config["INTERFACE_ADDRESS"],
            self.config["INTERFACE_PORT"],
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
