"""
Middleware Manager
"""
import logging
import pprint
from typing import TYPE_CHECKING, Dict

from bifrost.base import BaseManager

if TYPE_CHECKING:
    from bifrost.service import Service

logger = logging.getLogger(__name__)


class MiddlewareManager(BaseManager):
    """
    Middleware Manager
    """

    name = "Middleware Manager"
    setting_prefix = "MIDDLEWARE_MANAGER_"

    def __init__(self, service: Service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service: Service
        """
        super(MiddlewareManager, self).__init__(service, name, setting_prefix)

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
