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
from asyncio.events import get_event_loop
from asyncio.protocols import Protocol
from struct import pack, unpack
from typing import List, NamedTuple, Optional

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.base.protocols import Socks5Mixin
from bifrost.utils.misc import load_object


class VIMSMessage(NamedTuple):
    """
    Version Identifier/Method Selection Message
    """

    VER: int
    NMETHODS: int
    METHODS: List[int]


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


class Socks5Protocol(ProtocolMixin, Socks5Mixin, Protocol, LoggerMixin):
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

        client_addr: str
        client_port: int
        client_addr, client_port = self.transport.get_extra_info("peername")[:2]

        if self.state == self.INIT:
            self.logger.debug(
                "[AUTH] [%s] [%s:%s] sent: %s",
                id(self.transport),
                client_addr,
                client_port,
                repr(data),
            )
            vims_message = VIMSMessage(
                VER=data[0], NMETHODS=data[1], METHODS=list(data[2:])
            )
            assert vims_message.VER == 0x05

            ms_message = MSMessage(VER=0x05, METHOD=0x00)
            self.transport.write(pack("!BB", *ms_message))  # no auth
            self.state = self.HOST

        elif self.state == self.HOST:

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
            assert socks5_request.VER == 0x05 and socks5_request.CMD == 0x01

            self.logger.debug(
                "[HOST] [%s] [%s:%s] [%s:%s] sent: %s",
                id(self.transport),
                client_addr,
                client_port,
                str(socks5_request.DST_ADDR, encoding="utf-8"),
                socks5_request.DST_PORT,
                repr(data),
            )
            asyncio.create_task(
                self.connect(socks5_request.DST_ADDR, socks5_request.DST_PORT)
            )
            self.state = self.DATA

        elif self.state == self.DATA:
            self.logger.debug(
                "[DATA] [%s] [%s:%s] sent: %s bytes",
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
            VER=0x05, REP=0x00, RSV=0x00, ATYP=0x01, BND_ADDR=host, BND_PORT=port
        )
        self.transport.write(pack("!BBBBIH", *reply_message))
