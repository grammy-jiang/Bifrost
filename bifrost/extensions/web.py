import logging
from typing import Any

from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings

logger = logging.getLogger(__name__)

app = Sanic("Bifrost Web")


@app.route("/")
async def test(request: Request):
    return json({"hello": "world"})


class Web(BaseExtension):
    def __init__(self, service: Service, settings: Settings):
        super(Web, self).__init__(service, settings)

        self.server = app.create_server(
            host="0.0.0.0", port=8000, return_asyncio_server=True
        )

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
