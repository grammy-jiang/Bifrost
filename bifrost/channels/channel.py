import logging
from asyncio.events import AbstractEventLoop
from typing import TYPE_CHECKING, Type

from bifrost.settings import Settings
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
        self.loop: Type[AbstractEventLoop] = service.loop

        self.settings: Settings = settings
        self.role: str = settings["ROLE"]

        self.name: str = kwargs["name"]

        if self.role == "client":
            self.interface_protocol: str = kwargs["INTERFACE_PROTOCOL"]
            self.cls_interface_protocol: Type[Protocol] = load_object(
                self.interface_protocol
            )
            self.interface_address: str = kwargs["INTERFACE_ADDRESS"]
            self.interface_port: int = kwargs["INTERFACE_PORT"]

    @classmethod
    def from_service(cls, service: Type["Service"], **kwargs):
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings, **kwargs)
        return obj

    def _get_interface_protocol(self) -> Type["Protocol"]:
        if self.role != "client":
            raise NotImplementedError

        return self.cls_interface_protocol.from_service(self)

    def register(self):
        if self.role == "client":
            server = self.loop.create_server(
                self._get_interface_protocol,
                self.interface_address,
                self.interface_port,
            )
            self.loop.run_until_complete(server)
            logger.info(
                'Protocol "%s" is going to listen on the interface: %s:%s',
                self.interface_protocol,
                self.interface_address,
                self.interface_port,
            )
