"""
Channel
"""
from __future__ import annotations

import logging
from asyncio.base_events import Server
from asyncio.events import AbstractEventLoop
from typing import TYPE_CHECKING, Optional

from bifrost.settings import Settings
from bifrost.signals import loop_started, loop_stopped
from bifrost.signals.manager import SignalManager
from bifrost.utils.loop import get_event_loop
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.service import Service
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
        self._loop: AbstractEventLoop = get_event_loop(settings)

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

        self.server: Optional[Server] = None

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

        service.signal_manager.connect(obj.start, loop_started)
        service.signal_manager.connect(obj.stop, loop_stopped)
        return obj

    async def start(self, sender) -> None:  # pylint: disable=unused-argument
        """

        :param sender:
        :return:
        :rtype: None
        """
        self.server = await self._loop.create_server(
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

    async def stop(self, sender) -> None:  # pylint: disable=unused-argument
        """

        :param sender:
        :return:
        :rtype: None
        """
        self.server.close()
        await self.server.wait_closed()
