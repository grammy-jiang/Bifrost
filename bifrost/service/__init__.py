"""
Service module
"""
from __future__ import annotations

import asyncio
import logging
import platform
import pprint
import ssl
from asyncio.events import AbstractEventLoop
from datetime import datetime
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM
from typing import Dict, Type, Union

from bifrost.channels.channel import Channel
from bifrost.settings import Settings
from bifrost.signals import loop_started, loop_stopped
from bifrost.signals.manager import SignalManager
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
        self._get_runtime_info()

        self.start_time: datetime = datetime.now()

        self.settings: Settings = settings

        self.loop: Type[AbstractEventLoop] = get_event_loop(settings)
        logger.info(
            "In this service the loop is adopted from: %s", settings["LOOP"].upper()
        )

        self.signal_manager: SignalManager = load_object(
            settings["CLS_SIGNAL_MANAGER"]
        ).from_service(self)

        self.extension_manager: Type[Manager] = load_object(
            settings["CLS_MIDDLEWARE_MANAGER"]
        ).from_service(self)

        self.middleware_manager: Type[Manager] = load_object(
            settings["CLS_EXTENSION_MANAGER"]
        ).from_service(self)

        self.channels: Dict[str, Type[Channel]] = self._get_channels()

        self._configure_loop()

    @classmethod
    def from_settings(cls, settings: Settings):
        obj = cls(settings)
        return obj

    def _get_runtime_info(self):
        logger.info(
            "Platform: %(platform)s", {"platform": pprint.pformat(platform.platform())}
        )
        logger.info(
            "Platform details:\n%s",
            pprint.pformat(
                {
                    "OpenSSL": ssl.OPENSSL_VERSION,
                    "architecture": platform.architecture(),
                    "machine": platform.machine(),
                    "node": platform.node(),
                    "processor": platform.processor(),
                    "python_build": platform.python_build(),
                    "python_compiler": platform.python_compiler(),
                    "python_branch": platform.python_branch(),
                    "python_implementation": platform.python_implementation(),
                    "python_revision": platform.python_revision(),
                    "python_version": platform.python_version(),
                    "release": platform.release(),
                    "system": platform.system(),
                    "version": platform.version(),
                }
            ),
        )
        logger.info(
            "Versions:\n%s", pprint.pformat({"Python": platform.python_version(),})
        )

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

    def _configure_loop(self) -> None:
        """

        :return:
        :rtype: None
        """
        signals = (SIGHUP, SIGQUIT, SIGTERM, SIGINT)

        for signal in signals:
            self.loop.add_signal_handler(
                signal,
                lambda s=signal: asyncio.create_task(self._stop(s)),
            )

    async def _stop(self, signal=None):
        self.signal_manager.send(loop_stopped, sender=self)

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
        """
        self.signal_manager.send(loop_started, sender=self)

        try:
            self.loop.run_forever()
        except Exception as exc:
            logger.exception(exc)
        finally:
            self.loop.close()
            logger.info("Bifrost service is shutdown successfully.")
