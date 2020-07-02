"""
Web Extension with Sanic

Refer:

* https://sanicframework.org/
* https://sanic.readthedocs.io/en/latest/
* https://github.com/huge-success/sanic
"""

from graphene.types.objecttype import ObjectType
from graphene.types.scalars import String
from graphene.types.schema import Schema
from graphql.execution.base import ResolveInfo
from graphql.execution.executors.asyncio import AsyncioExecutor
from sanic.app import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json
from sanic_graphql.graphqlview import GraphQLView

from bifrost.base import BaseComponent, LoggerMixin
from bifrost.utils.misc import load_object


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

        # configure GraphQL
        schema = Schema(
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

        self.server = None  # type: ignore

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
