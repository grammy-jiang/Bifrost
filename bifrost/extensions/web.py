"""
Web Extension with Sanic

Refer:

* https://sanicframework.org/
* https://sanic.readthedocs.io/en/latest/
* https://github.com/huge-success/sanic
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from graphene.types.objecttype import ObjectType
from graphene.types.scalars import String
from graphene.types.schema import Schema
from graphql.execution.base import ResolveInfo
from graphql.execution.executors.asyncio import AsyncioExecutor
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json
from sanic.server import AsyncioServer
from sanic_graphql.graphqlview import GraphQLView

from bifrost.extensions import BaseExtension
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.settings import Settings

logger = logging.getLogger(__name__)


class Query(ObjectType):
    """
    Query for GraphQL Schema
    """

    hello = String()

    @staticmethod
    def resolve_hello(  # pylint: disable=bad-continuation,unused-argument
        parent, info: ResolveInfo
    ) -> str:
        """

        :param parent:
        :type parent:
        :param info:
        :type info: ResolveInfo
        :return:
        :rtype: str
        """
        return "world"


class Web(BaseExtension):
    """
    Web Extension
    """

    name = "Web"

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
        self.app.config["SERVICE"] = self.service

        # configure normal route
        self.app.add_route(self.home, "/")

        # configure GraphQL
        schema: Schema = Schema(
            **{
                k.replace("GRAPHQL_SCHEMA_", "").lower(): load_object(v)
                for k, v in self.config.items()
                if k.startswith("GRAPHQL_SCHEMA_")
            }
        )
        self.app.register_listener(
            listener=lambda app, loop: app.add_route(
                GraphQLView.as_view(
                    schema=schema, graphiql=True, executor=AsyncioExecutor(loop=loop),
                ),
                "/graphql",
            ),
            event="before_server_start",
        )

        self.server: AsyncioServer

    async def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        super(Web, self).service_started(sender)
        await self.start()

    async def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        await self.stop()

    async def start(self) -> None:
        """
        start this extension
        :return:
        :rtype: None
        """
        self.server = await self.app.create_server(
            debug=self.config["DEBUG"],
            host=self.config["ADDRESS"],
            port=self.config["PORT"],
            return_asyncio_server=True,
        )
        logger.info("Extension [%s] is running...", self.name)

    async def stop(self) -> None:
        """
        stop this extension
        :return:
        :rtype: None
        """
        self.server.close()
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
