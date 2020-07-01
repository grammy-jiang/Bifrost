"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from __future__ import annotations

from typing import Any, Dict


class ProtocolMixin:
    """
    Base Protocol
    """

    name: str = None
    setting_prefix: str = None

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
        self.settings = channel.settings

        if name:
            self.name: str = name
        if setting_prefix:
            self.setting_prefix: str = setting_prefix

        self.config: Dict[str, Any] = {
            key.replace(self.setting_prefix, ""): value
            for key, value in self.settings.items()
            if key.startswith(self.setting_prefix)
        }

    @classmethod
    def from_channel(
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
