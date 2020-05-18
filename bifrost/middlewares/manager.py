"""
Middleware Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.misc import load_object

logger = logging.getLogger(__name__)


class MiddlewareManager:
    """
    Middleware Manager
    """

    def __init__(self, service: Type[Service], settings: Settings):
        """

        :param service:
        :type service: Type[Service]
        :param settings:
        :type settings: Settings
        """
        self.service = service
        self.settings = settings

        self.cls_middlewares = dict(
            sorted(self.settings["MIDDLEWARES"].items(), key=lambda items: items[1])
        )
        self.middlewares = [
            load_object(cls).from_service(self.service)
            for cls in self.cls_middlewares.keys()
        ]
        logger.info("Enabled middlewares: \n%s", pprint.pformat(self.cls_middlewares))

    @classmethod
    def from_service(cls, service: Type[Service]) -> MiddlewareManager:
        """

        :param service:
        :type service: Type[Service]
        :return:
        :rtype: MiddlewareManager
        """
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
        return obj
