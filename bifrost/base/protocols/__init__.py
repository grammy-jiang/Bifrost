"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from bifrost.base.protocols.socks5 import Socks5Mixin
from bifrost.exceptions.protocol import TransportNotDefinedException

if TYPE_CHECKING:
    from asyncio.transports import Transport

    from bifrost.settings import Settings


class ProtocolMixin:
    """
    Base Protocol
    """

    name: str = None  # type: ignore
    setting_prefix: str = None  # type: ignore

    certificates = set()

    def __init__(self, channel, name: str = None, setting_prefix: str = None):
        """

        :param channel:
        :type channel:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        self.channel = channel

        if name:
            self.name: str = name
        if setting_prefix:
            self.setting_prefix: str = setting_prefix

        self.config: Dict[str, Any] = {
            key.replace(self.setting_prefix, ""): value
            for key, value in self.settings.items()
            if key.startswith(self.setting_prefix)
        }

        self.config.update(channel.config)

        self._transport = None
        self._server_transport = None
        self._client_transport = None

    @classmethod
    def from_channel(  # pylint: disable=bad-continuation
        cls, channel, name: str = None, setting_prefix: str = None
    ) -> ProtocolMixin:
        """

        :param channel:
        :type channel:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        :return:
        :rtype: ProtocolMixin
        """
        obj = cls(channel, name, setting_prefix)
        return obj

    @property
    def settings(self) -> Settings:
        """

        :return:
        :rtype: Settings
        """
        return self.channel.settings

    @property
    def signal_manager(self):
        """

        :return:
        :rtype:
        """
        return self.channel.signal_manager

    @property
    def stats(self):
        """

        :return:
        :rtype:
        """
        return self.channel.stats

    @property
    def transport(self) -> Transport:
        """

        :return:
        :rtype: Transport
        """
        if not self._transport:
            raise TransportNotDefinedException
        return self._transport

    @transport.setter
    def transport(self, value):
        self._transport = value

    @property
    def server_transport(self) -> Transport:
        """

        :return:
        :rtype: Transport
        """
        if not self._server_transport:
            raise TransportNotDefinedException
        return self._server_transport

    @server_transport.setter
    def server_transport(self, value):
        self._server_transport = value

    @property
    def client_transport(self) -> Transport:
        """

        :return:
        :rtype: Transport
        """
        if not self._client_transport:
            raise TransportNotDefinedException
        return self._client_transport

    @client_transport.setter
    def client_transport(self, value):
        self._client_transport = value


__all__ = ["ProtocolMixin", "Socks5Mixin"]
