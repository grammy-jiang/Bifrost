"""
Middleware Manager
"""
import pprint
from typing import Dict

from bifrost.base import BaseComponent, LoggerMixin, ManagerMixin


class MiddlewareManager(LoggerMixin, ManagerMixin, BaseComponent):
    """
    Middleware Manager
    """

    manage = "MIDDLEWARES"
    name = "MiddlewareManager"
    setting_prefix = "MIDDLEWARE_MANAGER_"

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name:
        :param setting_prefix:
        :type setting_prefix:
        """
        super(MiddlewareManager, self).__init__(service, name, setting_prefix)

        self.logger.info(
            "Enabled middlewares: \n%s", pprint.pformat(self.cls_middlewares)
        )

    @property
    def cls_middlewares(self) -> Dict[str, int]:
        """
        Get all middlewares with priority in a dict
        :return:
        :rtype: Dict[str, int]
        """
        return self._cls_components

    @property
    def middlewares(self) -> Dict[str, object]:
        """
        Get all middlewares by names in a dict
        :return:
        :rtype: Dict[str, object]
        """
        return self._components

    def get_middleware(self, name: str) -> object:
        """
        Get a middleware by its name
        :param name:
        :type name: str
        :return:
        :rtype: object
        """
        return self.middlewares[name]
