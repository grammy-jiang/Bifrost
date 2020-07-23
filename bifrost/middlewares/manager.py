"""
Middleware Manager
"""
import pprint
from typing import Callable, Dict

from bifrost.base import BaseComponent, LoggerMixin, ManagerMixin, SingletonMeta
from bifrost.signals import (
    connection_lost,
    connection_made,
    data_received,
    data_sent,
    eof_received,
    pause_writing,
    resume_writing,
)


def middlewares(func: Callable) -> Callable:
    """
    A decorator for middlewares
    :param func:
    :return:
    """

    def _connection_made(protocol, *args, **kwargs):
        protocol.signal_manager.send(connection_made)
        transport = args[0]
        protocol.transport = transport
        protocol.stats.increase(f"connections/{protocol.channel.name}/{protocol.name}")
        if protocol.role == "interface":
            if protocol.config["INTERFACE_SSL_CERT_FILE"]:
                protocol.logger.debug(
                    "[%s] [CONN] [%s:%s] connected with name [%s], "
                    "version [%s], "
                    "secret bits [%s]",
                    hex(id(protocol))[-4:],
                    *protocol.info_peername,
                    *transport.get_extra_info("cipher"),
                )
            else:
                protocol.logger.debug(
                    "[%s] [CONN] [%s:%s] connected",
                    hex(id(protocol))[-4:],
                    *protocol.info_peername,
                )
        elif protocol.role == "client":
            if cipher := transport.get_extra_info("cipher"):
                protocol.logger.debug(
                    "[CONN] [%s:%s] connected with name [%s], "
                    "version [%s], "
                    "secret bits [%s]",
                    *transport.get_extra_info("peername")[:2],
                    *cipher,
                )
            else:
                protocol.logger.debug(
                    "[CONN] [%s:%s] connected",
                    *transport.get_extra_info("peername")[:2],
                )
        return protocol, args, kwargs

    def _connection_lost(protocol, *args, **kwargs):
        protocol.signal_manager.send(connection_lost)
        return protocol, args, kwargs

    def _pause_writing(protocol, *args, **kwargs):
        protocol.signal_manager.send(pause_writing)
        return protocol, args, kwargs

    def _resume_writing(protocol, *args, **kwargs):
        protocol.signal_manager.send(resume_writing)
        return protocol, args, kwargs

    def _data_received(protocol, *args, **kwargs):
        data = args[0]
        if protocol.role == "interface":
            protocol.signal_manager.send(data_sent)
            protocol.stats.increase("data/sent", len(data))
            protocol.stats.increase(f"data/{protocol.channel.name}/sent", len(data))
        elif protocol.role == "client":
            protocol.signal_manager.send(data_received)
            protocol.stats.increase("data/received", len(data))
            protocol.stats.increase(f"data/{protocol.channel.name}/received", len(data))
        return protocol, args, kwargs

    def _eof_received(protocol, *args, **kwargs):
        protocol.signal_manager.send(eof_received)
        return protocol, args, kwargs

    process = {
        "connection_made": _connection_made,
        "connection_lost": _connection_lost,
        "pause_writing": _pause_writing,
        "resume_writing": _resume_writing,
        "data_received": _data_received,
        "eof_received": _eof_received,
    }

    def process_middlewares(protocol, *args, **kwargs):
        """

        :param protocol:
        :param args:
        :param kwargs:
        :return:
        """
        protocol, args, kwargs = process[func.__name__](protocol, *args, **kwargs)
        return func(protocol, *args, **kwargs)

    return process_middlewares


class MiddlewareManager(
    LoggerMixin, ManagerMixin, BaseComponent, metaclass=SingletonMeta
):
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
