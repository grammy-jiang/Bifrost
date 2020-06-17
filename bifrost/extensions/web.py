"""
Web Extension with Sanic

Refer:

* https://sanicframework.org/
* https://sanic.readthedocs.io/en/latest/
* https://github.com/huge-success/sanic
"""
from __future__ import annotations

import logging
from typing import Any

from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json

from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings

logger = logging.getLogger(__name__)


class Web(BaseExtension):
    """
    Web Extension
    """

    name = "Bifrost Web"

    setting_prefix = "WEB_"

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(Web, self).__init__(service, settings)

        self.app = Sanic(self.name)
        self.app.config.update(self.config)
        self.app.add_route(self.home, "/", strict_slashes=True)
        self._configure_app()

    def _configure_app(self):
        """
        configure app of Sanic
        :return:
        """
        pass

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        server = self.app.create_server(
            host=self.config["ADDRESS"],
            port=self.config["PORT"],
            return_asyncio_server=True,
        )
        self._loop.create_task(server)
        logger.info("Extension [%s] is running...", self.name)

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is stopped.", self.name)

    async def home(  # pylint: disable=bad-continuation,unused-argument
        self, request: Request
    ) -> HTTPResponse:
        """

        :param request:
        :type request: Request
        :return:
        :rtype: HTTPResponse
        """
        return json({"hello": "world"})
