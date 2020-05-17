"""
Middleware Manager
"""
from __future__ import annotations

import logging
from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings

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
