"""
Web Extension with Sanic

Refer:

* https://sanicframework.org/
* https://sanic.readthedocs.io/en/latest/
* https://github.com/huge-success/sanic
"""
import ssl
from typing import Optional

from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json

from bifrost.base import BaseComponent, LoggerMixin


class Web(BaseComponent, LoggerMixin):
    """
    Web Extension
    """

    name = "Web"
    setting_prefix = "WEB_"

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        super(Web, self).__init__(service, name, setting_prefix)

        self.app = Sanic(self.name)
        self.app.config["SERVICE"] = self.service

        # configure normal route
        self.app.add_route(self.home, "/")

        self.server = None  # type: ignore

    async def start(self) -> None:
        """
        start this extension
        :return:
        :rtype: None
        """
        ssl_context: Optional[ssl.SSLContext]
        if self.config["SSL_CERT_FILE"]:
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(
                certfile=self.config["SSL_CERT_FILE"],
                keyfile=self.config["SSL_KEY_FILE"],
                password=self.config["SSL_PASSWORD"],
            )
        else:
            ssl_context = None

        self.server = await self.app.create_server(
            host=self.config["ADDRESS"],
            port=self.config["PORT"],
            debug=self.config["DEBUG"],
            ssl=ssl_context,
            return_asyncio_server=True,
        )
        self.logger.info("Extension [%s] is running...", self.name)

    async def stop(self) -> None:
        """
        stop this extension
        :return:
        :rtype: None
        """
        if self.server:
            self.server.close()
            self.logger.info("Extension [%s] is stopped.", self.name)

    async def home(  # pylint: disable=unused-argument
        self, request: Request
    ) -> HTTPResponse:
        """

        :param request:
        :type request: Request
        :return:
        :rtype: HTTPResponse
        """
        return json({"hello": "world"})
