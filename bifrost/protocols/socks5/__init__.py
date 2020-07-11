"""
Single socks5 proxy as an example

RFC 1928 - SOCKS Protocol Version 5
https://datatracker.ietf.org/doc/rfc1928/

RFC 3089 - A SOCKS-based IPv6/IPv4 Gateway Mechanism
https://datatracker.ietf.org/doc/rfc3089/
"""
from __future__ import annotations

import pprint
import socket
from asyncio.events import get_event_loop
from asyncio.protocols import Protocol
from functools import cached_property
from struct import pack, unpack
from typing import Callable, Optional, Tuple

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.exceptions.protocol import ProtocolVersionNotSupportedException
from bifrost.middlewares import middlewares
from bifrost.utils.misc import load_object, to_str

VERSION = 0x05  # Socks version

INIT, AUTH, HOST, DATA = 0, 1, 2, 3


def validate_version(func: Callable, version=VERSION) -> Callable:
    """
    A decorator to validate socks version

    :param func:
    :type func: Callable
    :param version:
    :type version: int
    :return:
    :rtype: Callable
    """

    def validate(protocol: Socks5Protocol, data: bytes) -> Callable:
        """

        :param protocol:
        :type protocol: Socks5Protocol
        :param data:
        :type data: bytes
        :return:
        :rtype: Callable
        """
        ver: int = data[0]
        if ver != version:
            raise ProtocolVersionNotSupportedException
        return func(protocol, data)

    return validate


def parse_host_data(data: bytes) -> Tuple[int, int, int, int, bytes, int]:
    """
    SOCKS request

    +----+-----+-------+------+----------+----------+
    |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
    +----+-----+-------+------+----------+----------+
    | 1  |  1  | X'00' |  1   | Variable |    2     |
    +----+-----+-------+------+----------+----------+

    :param data:
    :type data: bytes
    :return:
    :rtype: Tuple[int, int, int, int, bytes, int]
    """
    ver: int = data[0]
    cmd: int = data[1]
    rsv: int = data[2]
    atyp: int = data[3]

    dst_addr: bytes
    nxt: int
    if atyp == 1:  # ipv4
        dst_addr, nxt = socket.inet_ntop(socket.AF_INET, data[4:8]), 8
    elif atyp == 3:  # domain
        length = data[4]
        dst_addr, nxt = data[5 : 5 + length], 5 + length
    elif atyp == 4:  # ipv6
        dst_addr, nxt = socket.inet_ntop(socket.AF_INET6, data[4:20]), 20

    dst_port: int = unpack("!H", data[nxt : nxt + 2])[0]

    return ver, cmd, rsv, atyp, dst_addr, dst_port


class Socks5Protocol(ProtocolMixin, Protocol, LoggerMixin):
    """
    A socks5 proxy server side
    """

    name = "Socks5"
    setting_prefix = "PROTOCOL_SOCKS5_"

    state = INIT

    @middlewares
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
            self.logger.debug("[CONN] [%s:%s] connected", *self.info_peername)
        else:
            self.logger.debug(
                "[CONN] [%s:%s] connected with name [%s], version [%s], secret bits [%s]",
                *self.info_peername,
                *transport.get_extra_info("cipher"),
            )

    @middlewares
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
        self.client_transport.close()
        self.transport.close()

    @middlewares
    def data_received(self, data: bytes) -> None:
        """
        Called when some data is received. data is a non-empty bytes object
        containing the incoming data.

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        if self.state == INIT:
            self._process_request_init(data)
        elif self.state == AUTH:
            self._process_request_auth(data)
        elif self.state == HOST:
            self._process_request_host(data)
        elif self.state == DATA:
            self._process_request_data(data)

    @cached_property
    def info_peername(self) -> Tuple[str, int]:
        """

        :return:
        :rtype: Tuple[str, int]
        """
        return self.transport.get_extra_info("peername")[:2]

    @validate_version
    def _process_request_init(self, data: bytes) -> None:
        """
        A version identifier/method selection message:

        +----+----------+----------+
        |VER | NMETHODS | METHODS  |
        +----+----------+----------+
        | 1  |    1     | 1 to 255 |
        +----+----------+----------+

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[INIT] [%s:%s] received: %s", *self.info_peername, repr(data),
        )

        ver, nmethods = data[:2]
        methods = list(data[2 : 2 + nmethods])

        available_auth_methods = sorted(
            set(self.config["AUTH_METHODS"]).intersection(set(methods)),
            key=lambda x: list(self.config["AUTH_METHODS"]).index(x),
        )

        try:
            auth_method = available_auth_methods[0]
        except IndexError:
            self.logger.debug(
                "No acceptable methods found. The following methods are supported:\n%s",
                pprint.pformat(self.config["AUTH_METHODS"]),
            )
            self.transport.write(pack("!BB", VERSION, 0xFF))  # NO ACCEPTABLE METHODS
            self.transport.close()
        else:
            self.transport.write(pack("!BB", VERSION, auth_method))
            self.cls_auth_method = load_object(self.config["AUTH_METHODS"][auth_method])
            self.state = self.cls_auth_method.transit_to

    def _process_request_auth(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[AUTH] [%s:%s] received: %s", *self.info_peername, repr(data),
        )
        auth_method = self.cls_auth_method.from_protocol(self)
        auth_method.auth(data)

    async def _connect(self, hostname: bytes, port: int) -> None:
        """

        :param hostname:
        :type hostname: bytes
        :param port:
        :type port: int
        :return:
        :rtype: None
        """
        cls_client = load_object(self.config["CLIENT_PROTOCOL"])

        loop = get_event_loop()

        client_transport, client_protocol = await loop.create_connection(
            lambda: cls_client.from_channel(self.channel), hostname, port,
        )

        client_protocol.server_transport = self.transport
        self.client_transport = client_transport

        bnd_addr: str
        bnd_port: int
        bnd_addr, bnd_port = client_transport.get_extra_info("sockname")

        bnd_addr: int = unpack("!I", socket.inet_aton(bnd_addr))[0]

        try:
            self.transport.write(
                pack("!BBBBIH", VERSION, 0x00, 0x00, 0x01, bnd_addr, bnd_port)
            )
        except Exception as exc:
            self.logger.error("Bind address: %s:%s", bnd_addr, bnd_port)
            self.logger.error(exc)

    @validate_version
    def _process_request_host(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """

        ver, cmd, rsv, atyp, dst_addr, dst_port = parse_host_data(data)
        assert cmd == 0x01

        self.logger.debug(
            "[HOST] [%s:%s] [%s:%s] received: %s",
            *self.info_peername,
            to_str(dst_addr),
            dst_port,
            repr(data),
        )
        loop = get_event_loop()
        loop.create_task(self._connect(dst_addr, dst_port))
        self.state = DATA

    def _process_request_data(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[DATA] [%s:%s] received: %s bytes", *self.info_peername, len(data),
        )
        self.client_transport.write(data)
