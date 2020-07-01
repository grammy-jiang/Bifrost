"""
Bifrost Client

This is a simple client - just send the tcp package to the server
"""
import asyncio
from socket import gaierror
from typing import Optional, Tuple

from bifrost.base import LoggerMixin
from bifrost.protocols import ClientProtocol, Protocol
from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop


class Client(ClientProtocol, LoggerMixin):
    """
    The simple client of proxy
    """

    def __init__(self, channel, settings):
        """

        :param channel:
        :type channel:
        :param settings:
        :type settings:
        """
        super(Client, self).__init__(channel, settings)

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


class Interface(Protocol, LoggerMixin):
    """
    A socks5 proxy server side
    """

    def __init__(self, channel, settings):
        """

        :param channel:
        :type channel:
        :param settings:
        :type settings: Settings
        """
        super(Interface, self).__init__(channel, settings)

        self.client_transport = None

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

        self.logger.debug(
            "[SERVER] [DATA] [%s] [%s:%s] sent: %s bytes",
            id(self.transport),
            client_addr,
            client_port,
            len(data),
        )

        asyncio.create_task(self.send_data(data))

    async def send_data(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        if self.client_transport is None:
            hostname, port = self.channel.cls_client_protocol.get_hostname_port(
                self.channel,
                self.channel.client_protocol_address,
                self.channel.client_protocol_port,
            )

            loop = get_event_loop(self.settings)
            try:
                transport, client = await loop.create_connection(
                    lambda: self.channel.cls_client_protocol.from_channel(self.channel),
                    hostname,
                    port,
                )
            except gaierror as exc:
                self.logger.error("[%s:%s] is not found.", hostname, port)
                self.logger.exception(exc)
            else:
                client.server_transport = self.transport
                self.client_transport = transport

        self.client_transport.write(data)
