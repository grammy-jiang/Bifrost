"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from __future__ import annotations

from asyncio.protocols import Protocol as _Protocol
from asyncio.transports import BaseTransport
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bifrost.channels.channel import Channel
    from bifrost.service import Service
    from bifrost.settings import Settings
    from bifrost.signals.manager import SignalManager


class Protocol(_Protocol):
    """
    Base Protocol
    """

    def __init__(self, channel: Channel, settings: Settings):
        """

        :param channel:
        :type channel: Channel
        :param settings:
        :type settings: Settings
        """
        super(Protocol, self).__init__()
        self.name: str = channel.name
        self.settings: Settings = settings

        self.service: Service = channel.service
        self.channel: Channel = channel

        self.transport: BaseTransport

    @classmethod
    def from_channel(cls, channel: Channel) -> Protocol:
        """

        :param channel:
        :type channel: Channel
        :return:
        :rtype: Protocol
        """
        settings = channel.settings
        obj = cls(channel, settings)
        return obj

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


class ClientProtocol(Protocol):
    """
    Base Client Protocol
    """

    @staticmethod
    def get_hostname_port(channel: Channel, hostname: str, port: int):
        """
        A classmethod to get hostname and port to connect with this client
        protocol
        :param channel:
        :param hostname:
        :param port:
        :return:
        """
        raise NotImplementedError
