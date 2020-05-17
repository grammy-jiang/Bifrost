"""
Service module
"""
from abc import ABC, abstractmethod

from bifrost.settings import Settings


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

    @abstractmethod
    def start(self):
        """
        Start this service
        :return:
        """
