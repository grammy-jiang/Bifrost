"""
Middleware Manager
"""
import pprint
from typing import Callable, Dict

from bifrost.base import BaseComponent, LoggerMixin, ManagerMixin


def middlewares(func: Callable) -> Callable:
    """
    A decorator for middlewares
    :param func:
    :return:
    """

    def process_middlewares(protocol, *args, **kwargs):
        """

        :param protocol:
        :param args:
        :param kwargs:
        :return:
        """
        if func.__name__ == "connection_made":
            transport = args[0]
            protocol.transport = transport
            protocol.stats.increase(f"connections/{protocol.name}")
        elif func.__name__ == "connection_lost":
            pass
        elif func.__name__ == "pause_writing":
            pass
        elif func.__name__ == "resume_writing":
            pass
        elif func.__name__ == "data_received":
            data = args[0]
            if protocol.role == "interface":
                protocol.stats.increase("data/sent", len(data))
                protocol.stats.increase(f"data/{protocol.name}/sent", len(data))
            elif protocol.role == "client":
                protocol.stats.increase("data/received", len(data))
                protocol.stats.increase(f"data/{protocol.name}/received", len(data))
        elif func.__name__ == "eof_received":
            pass

        return func(protocol, *args, **kwargs)

    return process_middlewares


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
