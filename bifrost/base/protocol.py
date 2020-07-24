"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Dict, Set

from bifrost.exceptions.protocol import TransportNotDefinedException

if TYPE_CHECKING:
    from asyncio.transports import Transport

    from bifrost.settings import Settings


class ProtocolMixin:
    """
    Base Protocol
    """

    name: str = None  # type: ignore
    role: str = None  # type: ignore
    setting_prefix: str = None  # type: ignore

    certificates: Set[str] = set()

    def __init__(
        self, channel, name: str = None, role: str = None, setting_prefix: str = None
    ):
        """

        :param channel:
        :type channel:
        :param name:
        :type name: str
        :param role:
        :type role: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        self.channel = channel

        if name:
            self.name: str = name
        if role:
            self.role: str = role
        if setting_prefix:
            self.setting_prefix: str = setting_prefix

        self._transport = None
        self._server_transport = None
        self._client_transport = None

    @classmethod
    def from_channel(
        cls, channel, name: str = None, role: str = None, setting_prefix: str = None
    ) -> ProtocolMixin:
        """

        :param channel:
        :type channel:
        :param name:
        :type name: str
        :param role:
        :type role: str
        :param setting_prefix:
        :type setting_prefix: str
        :return:
        :rtype: ProtocolMixin
        """
        obj = cls(channel, name, role, setting_prefix)
        return obj

    @functools.cached_property
    def config(self):
        """
        The configuration of this protocol
        :return:
        """
        config: Dict[str, Any] = {
            key.replace(self.setting_prefix, ""): value
            for key, value in self.settings.items()
            if key.startswith(self.setting_prefix)
        }

        config.update(self.channel.config)

        return config

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
    def transport(self) -> Transport:
        """

        :return:
        :rtype: Transport
        """
        if not self._transport:
            raise TransportNotDefinedException
        return self._transport

    @transport.setter
    def transport(self, value) -> None:
        """

        :param value:
        :type value:
        :return:
        :rtype: None
        """
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
    def server_transport(self, value) -> None:
        """

        :param value:
        :type value:
        :return:
        :rtype: None
        """
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
    def client_transport(self, value) -> None:
        """

        :param value:
        :type value:
        :return:
        :rtype: None
        """
        self._client_transport = value

    @property
    def socket(self):
        return self.transport.get_extra_info("socket")

    @property
    def server_socket(self):
        return self.server_transport.get_extra_info("socket")

    @property
    def client_socket(self):
        return self.client_transport.get_extra_info("socket")


__all__ = ["ProtocolMixin"]
