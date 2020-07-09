"""
Socks5 Protocol Mixin
"""
from __future__ import annotations

import pprint
import socket
from asyncio.events import get_event_loop
from struct import pack, unpack
from typing import NamedTuple, Tuple

from bifrost.base import LoggerMixin
from bifrost.utils.misc import load_object, to_str

VERSION = 0x05  # Socks version

INIT, AUTH, HOST, DATA = 0, 1, 2, 3


class MSMessage(NamedTuple):
    """
    METHOD selection message
    """

    VER: int
    METHOD: int


class SRMessage(NamedTuple):
    """
    SOCKS request
    o  VER  protocol version: X'05'
    o  CMD
        o   CONNECT X'01'
        o   BIND X'02'
        o   UDP ASSOCIATE X'03'
    o  RSV  RESERVED
    o  ATYP address type of following address
        o   IP V4 address: X'01'
        o   DOMAINNAME: X'03'
        o   IP V6 address: X'04'
    o  DST.ADDR desired destination address
    o  DST.PORT desired destination port in network octet order
    """

    VER: int
    CMD: int
    RSV: int
    ATYP: int
    DST_ADDR: bytes
    DST_PORT: int


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

        transport, client = await loop.create_connection(
            lambda: cls_client.from_channel(self.channel), hostname, port,
        )

        client.server_transport = self.transport
        self.client_transport = transport

        host_ip: str
        port: int
        host_ip, port = transport.get_extra_info("sockname")

        host: int = unpack("!I", socket.inet_aton(host_ip))[0]

        reply_message = RMessage(
            VER=VERSION, REP=0x00, RSV=0x00, ATYP=0x01, BND_ADDR=host, BND_PORT=port
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
            "[INIT] [%s:%s] received: %s", *self._get_client_info(), repr(data),
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
            "[AUTH] [%s:%s] received: %s", *self._get_client_info(), repr(data),
        )
        auth_method = self.cls_auth_method.from_protocol(self)
        auth_method.auth(data)

    def _process_request_host(self, data: bytes):
        """

        :param data:
        :type data: bytes
        :return:
        """

        def _get_socks5_request(data: bytes) -> SRMessage:
            atype: int = data[3]
            dst_addr: bytes
            nxt: int
            if atype == 1:  # ipv4
                dst_addr, nxt = socket.inet_ntop(socket.AF_INET, data[4:8]), 8
            elif atype == 3:  # domain
                length = data[4]
                dst_addr, nxt = data[5 : 5 + length], 5 + length
            elif atype == 4:  # ipv6
                dst_addr, nxt = socket.inet_ntop(socket.AF_INET6, data[4:20]), 20
            dst_port: int = unpack("!H", data[nxt : nxt + 2])[0]

            return SRMessage(*data[:4], DST_ADDR=dst_addr, DST_PORT=dst_port)

        socks5_request = _get_socks5_request(data)
        assert socks5_request.VER == VERSION and socks5_request.CMD == 0x01

        self.logger.debug(
            "[HOST] [%s:%s] [%s:%s] received: %s",
            *self._get_client_info(),
            to_str(socks5_request.DST_ADDR),
            socks5_request.DST_PORT,
            repr(data),
        )
        loop = get_event_loop()
        loop.create_task(self.connect(socks5_request.DST_ADDR, socks5_request.DST_PORT))
        self.state = DATA

    def _process_request_data(self, data: bytes):
        """

        :param data:
        :type data: bytes
        :return:
        """
        self.logger.debug(
            "[DATA] [%s:%s] received: %s bytes", *self._get_client_info(), len(data),
        )
        self.client_transport.write(data)

    def _get_client_info(self) -> Tuple[str, int]:
        """

        :return:
        :rtype: Tuple[str, int]
        """
        return self.transport.get_extra_info("peername")[:2]
