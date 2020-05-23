"""
Service module
"""
from __future__ import annotations

import logging
import pprint
from asyncio.events import AbstractEventLoop
from typing import Dict, Type, Union

from bifrost.channels.channel import Channel
from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop
from bifrost.utils.manager import Manager
from bifrost.utils.misc import load_object

logger = logging.getLogger(__name__)


class Service:
    """
    The abstract class of Service
    """

    def __init__(self, settings: Settings):
        """
        Initialize with Settings
        :param settings:
        :type settings: Settings
        """
        self.settings: Settings = settings
        self.role: str = settings["ROLE"]
        logger.info("This service is running in role: %s", self.role.upper())

        self.loop: Type[AbstractEventLoop] = get_event_loop(settings)
        logger.info(
            "In this service the loop is adopted from: %s", settings["LOOP"].upper()
        )

        self.extension_manager: Type[Manager] = load_object(
            settings["MIDDLEWARE_MANAGER"]
        ).from_service(self)

        self.middleware_manager: Type[Manager] = load_object(
            settings["EXTENSION_MANAGER"]
        ).from_service(self)

        self.channels: Dict[str, Type[Channel]] = self._get_channels()

    @classmethod
    def from_settings(cls, settings: Settings):
        obj = cls(settings)
        return obj

    def _get_channels(self) -> Dict[str, Type[Channel]]:
        """

        :return:
        :rtype: Dict[str, Type[Channel]]
        """
        channels: Dict[str, Type[Channel]] = {}
        repr_channels: Dict = {}

        name: str
        channel: Dict[str, Union[str, int]]
        for name, channel in self.settings["CHANNELS"].items():
            channels[name]: Type[Channel] = Channel.from_service(
                self, name=name, **channel
            )
            repr_channels[name] = channel

        logger.info("Enable channels:\n%s", pprint.pformat(repr_channels))

        return channels

    def start(self):
        """
        Start this service
        :return:
        """
        self.loop.run_forever()
