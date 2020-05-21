from __future__ import annotations

from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings


class Manager:
    def __init__(self, service: Type[Service], settings: Settings):
        """

        :param service:
        :type service: Type[Service]
        :param settings:
        :type settings: Settings
        """
        self.service = service
        self.settings = settings

    @classmethod
    def from_service(cls, service: Type[Service]) -> Manager:
        """

        :param service:
        :type service: Type[Service]
        :return:
        :rtype: Manager
        """
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
        return obj
