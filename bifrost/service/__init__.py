"""
Service module
"""
import logging
from asyncio.events import AbstractEventLoop
from typing import TYPE_CHECKING, Type

from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.utils.manager import Manager

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
        self.settings = settings
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

    @classmethod
    def from_settings(cls, settings: Settings):
        obj = cls(settings)
        return obj

    def start(self):
        """
        Start this service
        :return:
        """
        self.loop.run_forever()
