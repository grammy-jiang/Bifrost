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

from graphene.types.objecttype import ObjectType
from graphene.types.scalars import String
from graphene.types.schema import Schema
from graphql.execution.base import ResolveInfo
from graphql.execution.executors.asyncio import AsyncioExecutor
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json
from sanic_graphql.graphqlview import GraphQLView

from bifrost.extensions import BaseExtension
from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.misc import load_object

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
        self._configure_app()

    def _configure_app(self):
        """
        configure GraphQL for the app of Sanic
        :return:
        """
        self.app.config.update(self.config)

        # configure normal route
        self.app.add_route(self.home, "/")

        # configure GraphQL
        self.app.register_listener(
            listener=self._register_graphql, event="before_server_start"
        )

    def _register_graphql(self, app: Sanic, loop) -> None:
        """

        :param app:
        :type app: Sanic
        :param loop:
        :type loop:
        :return:
        :rtype: None
        """
        schema: Schema = Schema(
            **{
                k.replace("WEB_GRAPHQL_SCHEMA_", "").lower(): load_object(v)
                for k, v in self.settings.items()
                if k.startswith("WEB_GRAPHQL_SCHEMA_")
            }
        )
        self.app.add_route(
            GraphQLView.as_view(
                schema=schema, graphiql=True, executor=AsyncioExecutor(loop=loop)
            ),
            "/graphql",
        )

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
