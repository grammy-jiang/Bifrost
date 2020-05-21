"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from __future__ import annotations

from asyncio.protocols import Protocol as _Protocol
from asyncio.transports import BaseTransport
from typing import Optional, Type

from bifrost.service import Service
from bifrost.settings import Settings


class Protocol(_Protocol):
    def __init__(self, service: Type[Service], settings: Settings, *args, **kwargs):
        """

        :param service:
        :type service: Type[Service]
        :param settings:
        :type settings: Settings
        """
        super(Protocol, self).__init__(*args, **kwargs)
        self.service = service
        self.settings = settings

        self.transport: Optional[Type[BaseTransport]] = None

    @classmethod
    def from_service(cls, service: Type[Service], *args, **kwargs) -> Protocol:
        """

        :param service:
        :type service: Type[Service]
        :return:
        :rtype: Protocol
        """
        settings = getattr(service, "settings")
        obj = cls(service, settings, *args, **kwargs)
        return obj
