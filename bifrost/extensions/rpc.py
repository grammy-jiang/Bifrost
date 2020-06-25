"""
RPC

Refer to:
* https://grpc.io/
* https://grpc.github.io/grpc/python/index.html
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from grpc import ServerCredentials, ssl_server_credentials
from grpc.experimental.aio import Server, init_grpc_aio, server

from bifrost.extensions import BaseExtension

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.settings import Settings

logger = logging.getLogger(__name__)


class RPC(BaseExtension):
    """
    RPC
    """

    name = "RPC"
    setting_prefix = "RPC_"

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(RPC, self).__init__(service, settings)
        self.server: Server

    async def service_started(  # pylint: disable=bad-continuation,invalid-overridden-method
        self, sender: Any
    ) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        super(RPC, self).service_started(sender)

        init_grpc_aio()
        self.server = server()

        # TODO: add the gRPC servicer to server

        address = self.config["ADDRESS"]
        # secure mode
        if private_keys := self.config.get("SERVER_CREDENTIALS_PRIVATE_KEYS"):
            with open(private_keys, "rb") as file:
                keys: bytes = file.read()

            certs: Optional[bytes]
            if certificates := self.config.get("SERVER_CREDENTIALS_CERTIFICATES"):
                with open(certificates, "rb") as file:
                    certs = file.read()
            else:
                certs = None

            client_auth = self.config["SERVER_CREDENTIALS_CLIENT_AUTH"]

            credentials: ServerCredentials = ssl_server_credentials(
                keys, certs, client_auth
            )

            port = self.server.add_secure_port(address, credentials)
            logger.info(
                "Extension [%s] is running with certificate [%s] on port [%s]...",
                self.name,
                port,
                self.config["SERVER_CREDENTIALS_CERTIFICATES"],
            )
        # insecure mode
        else:
            port = self.server.add_insecure_port(address)
            logger.info("Extension [%s] is running on port [%s]...", self.name, port)

        await self.server.start()

    async def service_stopped(  # pylint: disable=bad-continuation,invalid-overridden-method
        self, sender: Any
    ) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        await self.server.stop(grace=self.config["STOP_GRACE"])
        logger.info("Extension [%s] is stopped.", self.name)
