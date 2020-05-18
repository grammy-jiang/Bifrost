"""
Service module
"""
from abc import ABC, abstractmethod
from typing import Type

from bifrost.extensions.manager import ExtensionManager
from bifrost.middlewares.manager import MiddlewareManager
from bifrost.settings import Settings
from bifrost.utils.misc import load_object


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

        self.extension_manager: Type[ExtensionManager] = load_object(
            settings["MIDDLEWARE_MANAGER"]
        ).from_service(self)

        self.middleware_manager: Type[MiddlewareManager] = load_object(
            settings["EXTENSION_MANAGER"]
        ).from_service(self)

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
