"""
Single socks5 proxy as an example

RFC 1928 - SOCKS Protocol Version 5
https://datatracker.ietf.org/doc/rfc1928/

RFC 3089 - A SOCKS-based IPv6/IPv4 Gateway Mechanism
https://datatracker.ietf.org/doc/rfc3089/
"""
from __future__ import annotations

import asyncio
import pprint
import socket
from asyncio.events import get_event_loop
from asyncio.protocols import Protocol
from functools import cached_property
from struct import pack, unpack
from typing import List, Optional, Tuple

from bifrost.base import LoggerMixin, ProtocolMixin, StatsMixin
from bifrost.exceptions.protocol import (
    ProtocolVersionNotSupportedException,
    Socks5CMDNotSupportedException,
    Socks5NetworkUnreachableException,
    Socks5NoAcceptableMethodsException,
    TransportNotDefinedException,
)
from bifrost.middlewares import middlewares
from bifrost.utils.misc import load_object, to_str

VERSION = 0x05  # Socks version


class Socks5State(LoggerMixin):
    """
    Base state for Socks5 protocol
    """

    def __init__(self, protocol: Socks5Protocol):
        """

        :param protocol:
        :type protocol: Socks5Protocol
        """
        self.protocol = protocol

    def _switch(self, state: str) -> None:
        """

        :param state:
        :type state: str
        :return:
        :rtype: None
        """
        self.protocol.state = self.protocol.states[state]

    async def data_received(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        raise NotImplementedError

    @staticmethod
    def validate(data: bytes) -> bool:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: bool
        """
        ver: int = data[0]
        return ver == VERSION


class Socks5StateInit(Socks5State):
    """
    INIT state
    """

    def switch(self) -> None:
        """
        Switch to Auth state
        :return:
        :rtype: None
        """
        return super(Socks5StateInit, self)._switch(
            self.protocol.cls_auth_method.next_state
        )

    async def data_received(self, data: bytes) -> None:
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
        if not self.validate(data):
            raise ProtocolVersionNotSupportedException

        self.logger.debug(
            "[%s] [INIT] [%s:%s] received: %s",
            hex(id(self.protocol))[-4:],
            *self.protocol.info_peername,
            repr(data),
        )

        nmethods: int = data[1]
        methods: List[int] = list(data[2 : 2 + nmethods])

        available_auth_methods = sorted(
            set(self.protocol.config["AUTH_METHODS"]).intersection(set(methods)),
            key=lambda x: list(self.protocol.config["AUTH_METHODS"]).index(x),
        )

        try:
            auth_method = available_auth_methods[0]
        except IndexError:
            self.logger.debug(
                "No acceptable methods found. "
                "The following methods are supported:\n%s",
                pprint.pformat(self.protocol.config["AUTH_METHODS"]),
            )
            self.protocol.transport.write(
                pack("!BB", VERSION, 0xFF)
            )  # NO ACCEPTABLE METHODS
            raise Socks5NoAcceptableMethodsException
        else:
            self.protocol.transport.write(pack("!BB", VERSION, auth_method))
            self.protocol.cls_auth_method = load_object(
                self.protocol.config["AUTH_METHODS"][auth_method]
            )


class Socks5StateAuth(Socks5State):
    """
    AUTH state
    """

    def switch(self):
        """
        Switch to HOST state
        :return:
        """
        super(Socks5StateAuth, self)._switch("HOST")

    async def data_received(self, data: bytes):
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[%s] [AUTH] [%s:%s] received: %s",
            hex(id(self.protocol))[-4:],
            *self.protocol.info_peername,
            repr(data),
        )
        # self.stats.increase(f"Authentication/{self.name}")
        auth_method = self.protocol.cls_auth_method.from_protocol(self.protocol)
        auth_method.auth(data)


class Socks5StateHost(Socks5State):
    """
    HOST State
    """

    supported_cmd = (
        0x01,  # connect
        # 0x02,  # TODO: bind
        # 0x03,  # TODO: udp associate
    )

    def switch(self):
        """
        Switch to DATA state
        :return:
        """
        super(Socks5StateHost, self)._switch("DATA")

    @staticmethod
    async def parse_host_data(data: bytes) -> Tuple[int, int, int, int, bytes, int]:
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

    async def data_received(self, data: bytes):
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        if not self.validate(data):
            raise ProtocolVersionNotSupportedException

        (
            ver,  # pylint: disable=unused-variable
            cmd,
            rsv,  # pylint: disable=unused-variable
            atyp,
            dst_addr,
            dst_port,
        ) = await self.parse_host_data(data)
        if cmd not in self.supported_cmd:
            raise Socks5CMDNotSupportedException

        self.logger.debug(
            "[%s] [HOST] [%s:%s] [%s:%s] received: %s",
            hex(id(self.protocol))[-4:],
            *self.protocol.info_peername,
            to_str(dst_addr),
            dst_port,
            repr(data),
        )

        cls_client = load_object(self.protocol.config["CLIENT_PROTOCOL"])

        try:
            (
                client_transport,
                client_protocol,
            ) = await self.protocol.loop.create_connection(
                lambda: cls_client.from_channel(self.protocol.channel, role="client"),
                dst_addr,
                dst_port,
            )
        except OSError as exc:
            if exc.args == (101, "Network is unreachable"):
                self.logger.error(
                    "The target is unreachable: %s:%s", dst_addr, dst_port,
                )
                # self.stats.increase(f"Error/{self.name}/{exc.strerror}")
                self.protocol.transport.write(
                    pack(
                        "!BBBBIH", VERSION, 0x03, 0x00, atyp, 0xFF, 0xFF
                    )  # Network unreachable
                )
                raise Socks5NetworkUnreachableException
            self.logger.exception(exc)
        else:
            client_protocol.server_transport = self.protocol.transport
            self.protocol.client_transport = client_transport

            bnd_addr_: str
            bnd_port: int
            bnd_addr_, bnd_port = client_transport.get_extra_info("sockname")

            bnd_addr: bytes = socket.inet_pton(self.protocol.socket.family, bnd_addr_)

            if self.protocol.socket.family == socket.AF_INET:
                address_type = 0x01
            elif self.protocol.socket.family == socket.AF_INET6:
                address_type = 0x03

            self.protocol.transport.write(
                pack(
                    f"!BBBB{len(bnd_addr)}sH",
                    VERSION,
                    0x00,
                    0x00,
                    address_type,
                    bnd_addr,
                    bnd_port,
                )
            )


class Socks5StateData(Socks5State):
    """
    DATA state
    """

    def switch(self):
        """
        Switch to DATA state
        :return:
        """
        super(Socks5StateData, self)._switch("DATA")

    async def data_received(self, data: bytes):
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[%s] [DATA] [%s:%s] received: %s bytes",
            hex(id(self.protocol))[-4:],
            *self.protocol.info_peername,
            len(data),
        )
        self.protocol.client_transport.write(data)


class Socks5Protocol(ProtocolMixin, Protocol, LoggerMixin, StatsMixin):
    """
    A socks5 proxy server side
    """

    name = "Socks5"
    role = "interface"
    setting_prefix = "PROTOCOL_SOCKS5_"

    def __init__(
        self, channel, name: str = None, role: str = None, setting_prefix: str = None
    ):
        super(Socks5Protocol, self).__init__(channel, name, role, setting_prefix)

        self.loop = get_event_loop()

        self.init = Socks5StateInit(self)
        self.auth = Socks5StateAuth(self)
        self.host = Socks5StateHost(self)
        self.data = Socks5StateData(self)

        self.states = {
            "INIT": self.init,
            "AUTH": self.auth,
            "HOST": self.host,
            "DATA": self.data,
        }

        self.state = self.init

        self.cls_auth_method = None

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
        try:
            self.client_transport.close()
        except TransportNotDefinedException:
            pass

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
        self.loop.create_task(self._data_received(data))

    async def _data_received(self, data: bytes) -> None:
        (result,) = await asyncio.gather(
            self.state.data_received(data), return_exceptions=True
        )
        if result is None:
            previous_state = self._get_state()
            self.state.switch()
            self.logger.debug(
                "[%s] [%s] State switched to [%s]",
                hex(id(self))[-4:],
                previous_state,
                self._get_state(),
            )
        elif isinstance(
            result,
            (Socks5NetworkUnreachableException, ProtocolVersionNotSupportedException),
        ):
            self.transport.close()
        elif isinstance(result, Exception):
            self.logger.exception(result)
            self.transport.close()

    @cached_property
    def info_peername(self) -> Tuple[str, int]:
        """

        :return:
        :rtype: Tuple[str, int]
        """
        return self.transport.get_extra_info("peername")[:2]

    def _get_state(self, state=None) -> str:
        """

        :return:
        :rtype: str
        """
        keys = list(self.states.keys())
        index = list(self.states.values()).index(state if state else self.state)
        return keys[index]
