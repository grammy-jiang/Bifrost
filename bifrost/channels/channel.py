import logging
from asyncio.base_events import Server
from asyncio.events import AbstractEventLoop
from typing import TYPE_CHECKING, Optional, Type

from bifrost.settings import Settings
from bifrost.signals import loop_started, loop_stopped
from bifrost.signals.manager import SignalManager
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.protocols import Protocol

logger = logging.getLogger(__name__)


class Channel:
    def __init__(self, service: Type["Service"], settings: Settings, **kwargs):
        """

        :param service:
        :type service: Type["Service"]
        :param settings:
        :type settings: Settings
        :param kwargs:
        """
        self.service: Service = service
        self.signal_manager: SignalManager = self.service.signal_manager
        self.loop: Type[AbstractEventLoop] = service.loop

        self.settings: Settings = settings
        self.role: str = settings["ROLE"]

        self.name: str = kwargs["name"]

        self.cryptographic_protocol = kwargs["CRYPTOGRAPHIC_PROTOCOL"]
        # The cryptographic address and port could be None if you want to use
        # Bifrost to directly connect to the target address, instead of going
        # through a server role node
        self.cryptographic_address: Optional[str] = kwargs.get("CRYPTOGRAPHIC_ADDRESS")
        self.cryptographic_port: Optional[int] = kwargs.get("CRYPTOGRAPHIC_PORT")

        if self.role == "client":
            self.interface_protocol: str = kwargs["INTERFACE_PROTOCOL"]
            self.cls_interface_protocol: Type[Protocol] = load_object(
                self.interface_protocol
            )
            self.interface_address: str = kwargs["INTERFACE_ADDRESS"]
            self.interface_port: int = kwargs["INTERFACE_PORT"]

            self.server: Optional[Server] = None

    @classmethod
    def from_service(cls, service: Type["Service"], **kwargs):
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings, **kwargs)

        service.signal_manager.connect(obj.start, loop_started)
        service.signal_manager.connect(obj.stop, loop_stopped)
        return obj

    async def start(self, sender):
        if self.role == "client":
            self.server: Server = await self.loop.create_server(
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

    async def stop(self, sender):
        try:
            self.server.close()
        except Exception as exc:
            logger.exception(exc)
        else:
            await self.server.wait_closed()
