from asyncio.events import AbstractEventLoop
from typing import TYPE_CHECKING, Type

from bifrost.settings import Settings
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.protocols import Protocol


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
