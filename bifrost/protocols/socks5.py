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
import asyncio
import socket
from asyncio.protocols import Protocol
from socket import gaierror
from struct import pack, unpack
from typing import Optional, Tuple

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.utils.loop import get_event_loop


class Client(ProtocolMixin, Protocol, LoggerMixin):
    """
    The simple client of proxy
    """

    name = "Socks5"
    setting_prefix = "PROTOCOL_SOCKS5_"

    def connection_made(self, transport) -> None:
        """

        :param transport:
        :type transport:
        :return:
        :rtype: None
        """
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
            "[CLIENT] [DATA] [%s:%s] recv: %s bytes",
            *self.transport.get_extra_info("peername"),
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

    @staticmethod
    def get_hostname_port(channel, hostname: str, port: int) -> Tuple[str, int]:
        """

        :param channel:
        :type channel:
        :param hostname:
        :type hostname: str
        :param port:
        :type port: int
        :return:
        :rtype: Tuple[str, int]
        """
        return hostname, port


class Socks5Protocol(ProtocolMixin, Protocol, LoggerMixin):
    """
    A socks5 proxy server side
    """

    name = "Socks5"
    setting_prefix = "PROTOCOL_SOCKS5_"

    INIT, HOST, DATA = 0, 1, 2

    def __init__(self, channel, name: str = None, setting_prefix: str = None):
        """

        :param channel:
        :type channel:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        super(Socks5Protocol, self).__init__(channel, name, setting_prefix)

        self.state = None

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
        self.logger.debug(
            "[SERVER] [CONN] [%s:%s] connected", *transport.get_extra_info("peername")
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
        self.stats.increase(f"{self.name}/data/sent", len(data))

        client_addr: str
        client_port: int
        client_addr, client_port = self.transport.get_extra_info("peername")

        if self.state == self.INIT:
            self.logger.debug(
                "[SERVER] [AUTH] [%s] [%s:%s] sent: %s",
                id(self.transport),
                client_addr,
                client_port,
                repr(data),
            )
            assert data[0] == 0x05
            self.transport.write(pack("!BB", 0x05, 0x00))  # no auth
            self.state = self.HOST

        elif self.state == self.HOST:
            ver: int  # protocol version: X'05'
            cmd: int  # o  CONNECT X'01'
            # o  BIND X'02'
            # o  UDP ASSOCIATE X'03'
            rsv: int  # RESERVED
            atype: int  # address type of following address
            # o  IP V4 address: X'01'
            # o  DOMAINNAME: X'03'
            # o  IP V6 address: X'04'
            ver, cmd, rsv, atype = data[:4]
            assert ver == 0x05 and cmd == 0x01

            if atype == 3:  # domain
                length = data[4]
                hostname, nxt = data[5 : 5 + length], 5 + length
            elif atype == 1:  # ipv4
                hostname, nxt = socket.inet_ntop(socket.AF_INET, data[4:8]), 8
            elif atype == 4:  # ipv6
                hostname, nxt = socket.inet_ntop(socket.AF_INET6, data[4:20]), 20
            port = unpack("!H", data[nxt : nxt + 2])[0]

            self.logger.debug(
                "[SERVER] [HOST] [%s] [%s:%s] [%s:%s] sent: %s",
                id(self.transport),
                client_addr,
                client_port,
                str(hostname, encoding="utf-8"),
                port,
                repr(data),
            )
            asyncio.create_task(self.connect(hostname, port))
            self.state = self.DATA

        elif self.state == self.DATA:
            self.logger.debug(
                "[SERVER] [DATA] [%s] [%s:%s] sent: %s bytes",
                id(self.transport),
                client_addr,
                client_port,
                len(data),
            )
            self.client_transport.write(data)

    async def connect(self, hostname: bytes, port: int) -> None:
        """

        :param hostname:
        :type hostname: bytes
        :param port:
        :type port: int
        :return:
        """
        _hostname, _port = self.channel.cls_client_protocol.get_hostname_port(
            self.channel, hostname, port
        )

        loop = get_event_loop(self.settings)
        try:
            transport, client = await loop.create_connection(
                lambda: self.channel.cls_client_protocol.from_channel(self.channel),
                _hostname,
                _port,
            )
        except gaierror as exc:
            self.logger.error("[%s:%s] is not found.", _hostname, _port)
            self.logger.exception(exc)
        else:
            client.server_transport = self.transport
            self.client_transport = transport

            host_ip: str
            port: int
            host_ip, port = transport.get_extra_info("sockname")

            host: int = unpack("!I", socket.inet_aton(host_ip))[0]
            self.transport.write(pack("!BBBBIH", 0x05, 0x00, 0x00, 0x01, host, port))
