"""
Channel
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from bifrost.signals import service_started, service_stopped
from bifrost.utils.loop import get_event_loop
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from asyncio.base_events import Server

    from bifrost.service import Service
    from bifrost.settings import Settings
    from bifrost.signals.manager import SignalManager
    from bifrost.protocols import Protocol

logger = logging.getLogger(__name__)


class Channel:
    """
    Channel
    """

    def __init__(self, service: Service, settings: Settings, **kwargs):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        :param kwargs:
        """
        self.service: Service = service
        self.signal_manager: SignalManager = self.service.signal_manager
        self.stats = service.stats

        self.settings: Settings = settings

        self.name: str = kwargs["name"]

        self.interface_protocol: str = kwargs["INTERFACE_PROTOCOL"]
        self.cls_interface_protocol: Protocol = load_object(self.interface_protocol)
        self.interface_address: str = kwargs["INTERFACE_ADDRESS"]
        self.interface_port: int = kwargs["INTERFACE_PORT"]

        self.client_protocol: str = kwargs["CLIENT_PROTOCOL"]
        self.cls_client_protocol: Protocol = load_object(self.client_protocol)
        self.client_protocol_address: Optional[str] = kwargs.get(
            "CLIENT_PROTOCOL_ADDRESS"
        )
        self.client_protocol_port: Optional[int] = kwargs.get("CLIENT_PROTOCOL_PORT")

        self.server: Server

    @classmethod
    def from_service(cls, service: Service, **kwargs) -> Channel:
        """

        :param service:
        :type service: Service
        :param kwargs:
        :return:
        :rtype: Channel
        """
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings, **kwargs)

        service.signal_manager.connect(obj.service_start, service_started)
        service.signal_manager.connect(obj.service_stop, service_stopped)
        return obj

    async def service_start(self, sender) -> None:  # pylint: disable=unused-argument
        """

        :param sender:
        :return:
        :rtype: None
        """
        loop = get_event_loop(self.settings)
        self.server = await loop.create_server(
            lambda: self.cls_interface_protocol.from_channel(self),
            self.interface_address,
            self.interface_port,
        )
        logger.info(
            "Protocol [%s] is listening on the interface: %s:%s",
            self.interface_protocol,
            self.interface_address,
            self.interface_port,
        )

    async def service_stop(self, sender) -> None:  # pylint: disable=unused-argument
        """

        :param sender:
        :return:
        :rtype: None
        """
        self.server.close()
        await self.server.wait_closed()
