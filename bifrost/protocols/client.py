"""
Bifrost Client

This is a simple client - just send the tcp package to the server
"""
import asyncio
import ssl
from asyncio.protocols import Protocol
from typing import Optional

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.utils.loop import get_event_loop
from bifrost.utils.misc import load_object


class Interface(ProtocolMixin, Protocol, LoggerMixin):
    """
    A socks5 proxy server side
    """

    name = "Interface"
    setting_prefix = "PROTOCOL_INTERFACE_"

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
            ssl_context: Optional[ssl.SSLContext]
            if self.config["CLIENT_SSL_CERT_FILE"]:
                ssl_context = ssl.create_default_context(
                    purpose=ssl.Purpose.SERVER_AUTH
                )
                ssl_context.load_cert_chain(
                    certfile=self.config["CLIENT_SSL_CERT_FILE"],
                    keyfile=self.config["CLIENT_SSL_KEY_FILE"],
                    password=self.config["CLIENT_SSL_PASSWORD"],
                )
            else:
                ssl_context = None

            cls_client = load_object(self.config["CLIENT_PROTOCOL"])

            loop = get_event_loop(self.settings)

            transport, client = await loop.create_connection(
                protocol_factory=lambda: cls_client.from_channel(self.channel),
                host=self.config.get("CLIENT_ADDRESS"),
                port=self.config.get("CLIENT_PORT"),
                ssl=ssl_context,
            )

            client.server_transport = self.transport
            self.client_transport = transport

        self.client_transport.write(data)
