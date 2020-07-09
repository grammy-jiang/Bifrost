"""
Socks5 Protocol Mixin
"""
from __future__ import annotations

import pprint
import socket
from asyncio.events import get_event_loop
from functools import cached_property
from struct import pack, unpack
from typing import NamedTuple, Tuple

from bifrost.base import LoggerMixin
from bifrost.utils.misc import load_object, to_str

VERSION = 0x05  # Socks version

INIT, AUTH, HOST, DATA = 0, 1, 2, 3


class RMessage(NamedTuple):
    """
    Reply message
    o  VER    protocol version: X'05'
    o  REP    Reply field:
        o  X'00' succeeded
        o  X'01' general SOCKS server failure
        o  X'02' connection not allowed by ruleset
        o  X'03' Network unreachable
        o  X'04' Host unreachable
        o  X'05' Connection refused
        o  X'06' TTL expired
        o  X'07' Command not supported
        o  X'08' Address type not supported
        o  X'09' to X'FF' unassigned
    o  RSV    RESERVED
    o  ATYP   address type of following address
        o  IP V4 address: X'01'
        o  DOMAINNAME: X'03'
        o  IP V6 address: X'04'
    o  BND.ADDR     server bound address
    o  BND.PORT     server bound port in network octet order
    """

    VER: int
    REP: int
    RSV: int
    ATYP: int
    BND_ADDR: int
    BND_PORT: int


class Socks5Mixin(LoggerMixin):
    """
    Socks5 Protocol Mixin
    """

    state = None
    auth_method = None

    def connection_made(self, transport) -> None:
        """

        :param transport:
        :type transport:
        :return:
        :rtype: None
        """
        self.state = INIT

    def data_received(self, data: bytes) -> None:
        """

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

    async def connect(self, hostname: bytes, port: int) -> None:
        """

        :param hostname:
        :type hostname: bytes
        :param port:
        :type port: int
        :return:
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

        reply_message = RMessage(
            VER=VERSION,
            REP=0x00,
            RSV=0x00,
            ATYP=0x01,
            BND_ADDR=bnd_addr,
            BND_PORT=bnd_port,
        )
        self.transport.write(pack("!BBBBIH", *reply_message))

    def _process_request_init(self, data: bytes):
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
        """
        self.logger.debug(
            "[INIT] [%s:%s] received: %s", *self.client_info, repr(data),
        )

        ver = data[0]
        nmethods = data[1]
        methods = list(data[2 : 2 + nmethods])

        assert ver == VERSION

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
            "[AUTH] [%s:%s] received: %s", *self.client_info, repr(data),
        )
        auth_method = self.cls_auth_method.from_protocol(self)
        auth_method.auth(data)

    def _process_request_host(self, data: bytes):
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
        """

        def parse_data(data: bytes) -> Tuple[int, int, int, int, bytes, int]:
            """

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

        ver, cmd, _, _, dst_addr, dst_port = parse_data(data)
        assert ver == VERSION and cmd == 0x01

        self.logger.debug(
            "[HOST] [%s:%s] [%s:%s] received: %s",
            *self.client_info,
            to_str(dst_addr),
            dst_port,
            repr(data),
        )
        loop = get_event_loop()
        loop.create_task(self.connect(dst_addr, dst_port))
        self.state = DATA

    def _process_request_data(self, data: bytes):
        """

        :param data:
        :type data: bytes
        :return:
        """
        self.logger.debug(
            "[DATA] [%s:%s] received: %s bytes", *self.client_info, len(data),
        )
        self.client_transport.write(data)

    @cached_property
    def client_info(self) -> Tuple[str, int]:
        """

        :return:
        :rtype: Tuple[str, int]
        """
        return self.transport.get_extra_info("peername")[:2]
