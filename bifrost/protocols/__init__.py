"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from asyncio.protocols import Protocol
from typing import Optional

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.middlewares import middlewares
from bifrost.protocols.client import Interface
from bifrost.protocols.socks5 import Socks5Protocol


class Client(ProtocolMixin, Protocol, LoggerMixin):
    """
    The simple client of proxy
    """

    name = "Client"
    setting_prefix = "PROTOCOL_CLIENT_"

    @middlewares
    def connection_made(self, transport) -> None:
        """

        :param transport:
        :type transport:
        :return:
        :rtype: None
        """
        if cipher := transport.get_extra_info("cipher"):
            self.logger.debug(
                "[CONN] [%s:%s] connected with name [%s], version [%s], secret bits [%s]",
                *transport.get_extra_info("peername")[:2],
                *cipher,
            )
        else:
            self.logger.debug(
                "[CONN] [%s:%s] connected", *transport.get_extra_info("peername")[:2]
            )

    @middlewares
    def data_received(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[DATA] [%s:%s] recv: %s bytes",
            *self.transport.get_extra_info("peername")[:2],
            len(data),
        )

        self.server_transport.write(data)

    @middlewares
    def connection_lost(self, exc: Optional[Exception]) -> None:
        """

        :param exc:
        :type exc: Optional[Exception]
        :return:
        :rtype: None
        """
        self.server_transport.close()


__all__ = ["Client", "Interface", "Socks5Protocol"]
