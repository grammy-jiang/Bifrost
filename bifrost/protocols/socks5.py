"""
Single socks5 proxy as an example

RFC 1928 - SOCKS Protocol Version 5
https://datatracker.ietf.org/doc/rfc1928/

RFC 1929 - Username/Password Authentication for SOCKS V5
https://datatracker.ietf.org/doc/rfc1929/

RFC 1961 - GSS-API Authentication Method for SOCKS Version 5
https://datatracker.ietf.org/doc/rfc1961/

RFC 3089 - A SOCKS-based IPv6/IPv4 Gateway Mechanism
https://datatracker.ietf.org/doc/rfc3089/
"""

from asyncio.protocols import Protocol
from typing import Optional

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.base.protocols import Socks5Mixin


class Socks5Protocol(ProtocolMixin, Socks5Mixin, Protocol, LoggerMixin):
    """
    A socks5 proxy server side
    """

    name = "Socks5"
    setting_prefix = "PROTOCOL_SOCKS5_"

    def connection_made(self, transport) -> None:
        """
        Called when a connection is made.

        The transport argument is the transport representing the connection. The
        protocol is responsible for storing the reference to its transport.

        :param transport:
        :type transport:
        :return:
        :rtype: None
        """
        if not self.config["INTERFACE_SSL_CERT_FILE"]:
            self.logger.debug(
                "[CONN] [%s:%s] connected", *transport.get_extra_info("peername")[:2]
            )
        else:
            self.logger.debug(
                "[CONN] [%s:%s] connected with name [%s], version [%s], secret bits [%s]",
                *transport.get_extra_info("peername")[:2],
                *transport.get_extra_info("cipher"),
            )
        self.stats.increase(f"{self.name}/connect")

        self.transport = transport
        self.state = self.INIT

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """
        Called when the connection is lost or closed.

        The argument is either an exception object or None. The latter means a
        regular EOF is received, or the connection was aborted or closed by this
        side of the connection.

        :param exc:
        :type exc: Optional[Exception]
        :return:
        :rtype: None
        """
        self.transport.close()

    def data_received(self, data: bytes) -> None:
        """
        Called when some data is received. data is a non-empty bytes object
        containing the incoming data.

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.stats.increase("data/sent", len(data))
        self.stats.increase(f"data/{self.name}/sent", len(data))

        super(Socks5Protocol, self).data_received(data)
