"""
Middleware Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.manager import Manager

logger = logging.getLogger(__name__)


class MiddlewareManager(Manager):
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
        super(MiddlewareManager, self).__init__(service, settings)

        self._register_components("MIDDLEWARES")
        logger.info("Enabled middlewares: \n%s", pprint.pformat(self.cls_components))
