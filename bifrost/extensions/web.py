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
from typing import Any, Dict

from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json

from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings

logger = logging.getLogger(__name__)

app = Sanic("Bifrost Web")


@app.route("/")
async def test(request: Request) -> HTTPResponse:  # pylint: disable=unused-argument
    """

    :param request:
    :type request: Request
    :return:
    :rtype: HTTPResponse
    """
    return json({"hello": "world"})


class Web(BaseExtension):
    """
    Web Extension
    """

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(Web, self).__init__(service, settings)

        self.server = app.create_server(
            host=settings["WEB_CONFIG_ADDRESS"],
            port=settings["WEB_CONFIG_PORT"],
            return_asyncio_server=True,
        )

    @classmethod
    def from_service(cls, service: Service) -> Web:
        """

        :param service:
        :return:
        """
        obj = super(Web, cls).from_service(service)

        settings: Settings = service.settings

        app_config: Dict = dict(
            starmap(
                lambda k, v: (k.replace("WEB_CONFIG_", ""), v),
                filter(lambda x: x[0].startswith("WEB_CONFIG_"), settings.items()),
            )
        )

        app.config.update(app_config)

        return obj

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        self._loop.create_task(self.server)
        logger.info("Extension [%s] is running...", self.__class__.__name__)

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is stopped.", self.__class__.__name__)
