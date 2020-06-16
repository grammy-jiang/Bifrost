"""
Web Extension with Sanic

Refer:

* https://sanicframework.org/
* https://sanic.readthedocs.io/en/latest/
* https://github.com/huge-success/sanic
"""
from __future__ import annotations

import logging
from itertools import starmap
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

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(Web, self).__init__(service, settings)

        self.app = Sanic(self.name)

        self.app_config = dict(
            starmap(
                lambda k, v: (k.replace("WEB_CONFIG_", ""), v),
                filter(lambda x: x[0].startswith("WEB_CONFIG_"), settings.items()),
            )
        )
        self.app.config.update(self.app_config)

        self.app.add_route(self.home, "/", strict_slashes=True)

        self.server = self.app.create_server(
            host=self.app_config["ADDRESS"],
            port=self.app_config["PORT"],
            return_asyncio_server=True,
        )

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        self._loop.create_task(self.server)
        logger.info("Extension [%s] is running...", self.name)

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is stopped.", self.name)

    async def home(
        self, request: Request
    ) -> HTTPResponse:  # pylint: disable=unused-argument
        """

        :param request:
        :type request: Request
        :return:
        :rtype: HTTPResponse
        """
        return json({"hello": "world"})
