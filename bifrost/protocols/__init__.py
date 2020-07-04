"""
Transports and Protocols
https://docs.python.org/3/library/asyncio-protocol.html
"""
from asyncio.protocols import Protocol
from typing import Optional

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.protocols.client import Interface
from bifrost.protocols.socks5 import Socks5Protocol


class Client(ProtocolMixin, Protocol, LoggerMixin):
    """
    The simple client of proxy
    """

    name = "Client"
    setting_prefix = "PROTOCOL_CLIENT_"

    def connection_made(self, transport) -> None:
        """

        :param transport:
        :type transport:
        :return:
        :rtype: None
        """
        if not self.config["CLIENT_SSL_CERT_FILE"]:
            self.logger.debug(
                "[CONN] [%s:%s] connected", *transport.get_extra_info("peername")[:2]
            )
        else:
            self.logger.debug(
                "[CONN] [%s:%s] connected with name [%s], version [%s], secret bits [%s]",
                *transport.get_extra_info("peername")[:2],
                *transport.get_extra_info("cipher"),
            )
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.stats.increase("data/received", len(data))
        self.stats.increase(f"{self.name}/data/received", len(data))

        self.logger.debug(
            "[DATA] [%s:%s] recv: %s bytes",
            *self.transport.get_extra_info("peername")[:2],
            len(data),
        )

        self.server_transport.write(data)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """

        :param exc:
        :type exc: Optional[Exception]
        :return:
        :rtype: None
        """
        self.server_transport.close()


__all__ = ["Client", "Interface", "Socks5Protocol"]
