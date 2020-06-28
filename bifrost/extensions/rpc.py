"""
RPC

Refer to:
* https://grpc.io/
* https://grpc.github.io/grpc/python/index.html
"""
from typing import Optional

from grpc import ServerCredentials, ssl_server_credentials
from grpc.experimental.aio import init_grpc_aio, server

from bifrost.base import BaseComponent, LoggerMixin


class RPC(BaseComponent, LoggerMixin):
    """
    RPC
    """

    name = "RPC"
    setting_prefix = "RPC_"

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        super(RPC, self).__init__(service, name, setting_prefix)

        self.server = None

    async def start(self) -> None:
        """

        :return:
        :rtype: None
        """
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

            port = self.server.add_secure_port(address, credentials)  # type: ignore
            self.logger.info(
                "Extension [%s] is running with certificate [%s] on port [%s]...",
                self.name,
                port,
                self.config["SERVER_CREDENTIALS_CERTIFICATES"],
            )
        # insecure mode
        else:
            port = self.server.add_insecure_port(address)  # type: ignore
            self.logger.info(
                "Extension [%s] is running on port [%s]...", self.name, port
            )

        await self.server.start()  # type: ignore

    async def stop(self) -> None:
        """

        :return:
        :rtype: None
        """
        if self.server:
            await self.server.stop(grace=self.config["STOP_GRACE"])
            self.logger.info("Extension [%s] is stopped.", self.name)
