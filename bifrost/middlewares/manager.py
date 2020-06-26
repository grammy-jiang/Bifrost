"""
Middleware Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import TYPE_CHECKING, Dict

from bifrost.base.manager import Manager

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.settings import Settings

logger = logging.getLogger(__name__)


class MiddlewareManager(Manager):
    """
    Middleware Manager
    """

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(MiddlewareManager, self).__init__(service, settings)

        self._register_components("MIDDLEWARES")
        logger.info("Enabled middlewares: \n%s", pprint.pformat(self._cls_components))

    @property
    def middlewares(self) -> Dict[str, object]:
        """
        get all middlewares in a dict
        :return:
        :rtype: Dict[str, object]
        """
        return self._components

    def get_middleware(self, name: str) -> object:
        """
        get a middleware by its name
        :param name:
        :type name: str
        :return:
        :rtype: object
        """
        return self.middlewares[name]
