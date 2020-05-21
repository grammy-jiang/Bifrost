"""
Service module
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type

from bifrost.settings import Settings
from bifrost.utils.misc import load_object
from bifrost.utils.loop import get_event_loop

if TYPE_CHECKING:
    from bifrost.utils.manager import Manager


class Service(ABC):
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

        self.extension_manager: Type["Manager"] = load_object(
            settings["MIDDLEWARE_MANAGER"]
        ).from_service(self)

        self.middleware_manager: Type["Manager"] = load_object(
            settings["EXTENSION_MANAGER"]
        ).from_service(self)

        self.loop = get_event_loop(settings)

    @classmethod
    def from_settings(cls, settings: Settings):
        obj = cls(settings)
        return obj

    @abstractmethod
    def start(self):
        """
        Start this service
        :return:
        """
        self.loop.run_forever()
