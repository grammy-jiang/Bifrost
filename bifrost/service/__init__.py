"""
Service module
"""
from __future__ import annotations

import asyncio
import logging
import pprint
from asyncio.events import AbstractEventLoop
from datetime import datetime
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM
from typing import Any, Dict

from bifrost.channels.channel import Channel
from bifrost.extensions.stats import Stats
from bifrost.extensions.manager import ExtensionManager
from bifrost.middlewares.manager import MiddlewareManager
from bifrost.settings import Settings
from bifrost.signals import service_started, service_stopped
from bifrost.signals.manager import SignalManager
from bifrost.utils.log import get_runtime_info
from bifrost.utils.loop import get_event_loop
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
        get_runtime_info()

        self.settings: Settings = settings

        # initial loop at the very beginning
        self.loop: AbstractEventLoop = get_event_loop(settings)
        logger.info(
            "In this service the loop is adopted from: %s", settings["LOOP"].upper()
        )

        self._configure_loop()

        self.signal_manager: SignalManager = load_object(
            settings["CLS_SIGNAL_MANAGER"]
        ).from_settings(settings)

        # Setup signals for Service, because Service can't setup Signal Manager
        # from classmethod from_settings
        self.signal_manager.connect(self.service_started, service_started)
        self.signal_manager.connect(self.service_stopped, service_stopped)

        self.extension_manager: ExtensionManager = load_object(
            settings["CLS_EXTENSION_MANAGER"]
        ).from_service(self)

        self.stats: Stats = self.extension_manager.get_extension(name="Stats")

        self.middleware_manager: MiddlewareManager = load_object(
            settings["CLS_MIDDLEWARE_MANAGER"]
        ).from_service(self)

        self.channels: Dict[str, Channel] = self._get_channels()

    @classmethod
    def from_settings(cls, settings: Settings) -> Service:
        """
        Initialize a Service instance by settings
        :param settings:
        :type settings: Settings
        :return:
        :rtype: Service
        """
        obj = cls(settings)
        return obj

    def _get_channels(self) -> Dict[str, Channel]:
        """

        :return:
        :rtype: Dict[str, Channel]
        """
        channels: Dict[str, Channel] = {}

        cls_channel: Channel = load_object(self.settings["CLS_CHANNEL"])

        for name, channel in self.settings["CHANNELS"].items():
            channels[name] = cls_channel.from_service(self, name=name, **channel)

        logger.info("Enable channels:\n%s", pprint.pformat(self.settings["CHANNELS"]))

        return channels

    def _configure_loop(self) -> None:
        """
        Add loop start signal call at the beginning of the loop, and also the
        quit signal call when signals received
        :return:
        :rtype: None
        """
        self.loop.call_soon_threadsafe(
            lambda: self.signal_manager.send(service_started, sender=self)
        )

        signals = (SIGHUP, SIGQUIT, SIGTERM, SIGINT)

        for signal in signals:
            self.loop.add_signal_handler(
                signal, lambda s=signal: asyncio.create_task(self._stop(s)),
            )

    async def _stop(self, signal=None):  # pylint: disable=unused-argument
        self.signal_manager.send(service_stopped, sender=self)

        await asyncio.sleep(1)

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks)

        self.loop.stop()

    def start(self) -> None:
        """
        Start this service
        :return:
        :rtype: None
        """
        self.stats["time/start"] = datetime.now()

        self.loop.run_forever()
        self.loop.close()
        logger.info("Bifrost service is shutdown successfully.")

    def service_started(self, sender: Any) -> None:  # pylint: disable=unused-argument
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Service [%s] is running...", self.__class__.__name__)

    def service_stopped(self, sender: Any) -> None:  # pylint: disable=unused-argument
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Service [%s] is going to stop...", self.__class__.__name__)
