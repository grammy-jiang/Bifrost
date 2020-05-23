"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from __future__ import annotations

from asyncio.protocols import Protocol as _Protocol
from asyncio.transports import BaseTransport
from typing import Optional, Type

from bifrost.channels.channel import Channel
from bifrost.service import Service
from bifrost.settings import Settings


class Protocol(_Protocol):
    def __init__(self, channel: Type[Channel], *args, **kwargs):
        """

        :param channel:
        :type channel: Type[Channel]
        :param args:
        :param kwargs:
        """
        super(Protocol, self).__init__(*args, **kwargs)
        self.channel: Type[Channel] = channel
        self.name: str = channel.name

        self.service: Type[Service] = channel.service
        self.settings: Settings = channel.settings

        self.transport: Optional[Type[BaseTransport]] = None

    @classmethod
    def from_channel(cls, channel: Type[Channel], *args, **kwargs) -> Protocol:
        """

        :param channel:
        :type channel: Type[Channel]
        :return:
        :rtype: Protocol
        """
        obj = cls(channel, *args, **kwargs)
        return obj
