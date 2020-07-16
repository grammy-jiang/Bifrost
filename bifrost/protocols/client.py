"""
Simple Client protocol
"""
from asyncio.protocols import Protocol
from typing import Optional

from bifrost.base import LoggerMixin, ProtocolMixin
from bifrost.middlewares import middlewares


class Client(ProtocolMixin, Protocol, LoggerMixin):
    """
    The simple client of proxy
    """

    name = "Client"
    role = "client"
    setting_prefix = "PROTOCOL_CLIENT_"

    @middlewares
    def connection_made(self, transport) -> None:
        """

        :param transport:
        :type transport:
        :return:
        :rtype: None
        """

    @middlewares
    def data_received(self, data: bytes) -> None:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: None
        """
        self.logger.debug(
            "[DATA] [%s:%s] recv: %s bytes",
            *self.transport.get_extra_info("peername")[:2],
            len(data),
        )

        self.server_transport.write(data)

    @middlewares
    def connection_lost(self, exc: Optional[Exception]) -> None:
        """

        :param exc:
        :type exc: Optional[Exception]
        :return:
        :rtype: None
        """
        self.server_transport.close()
