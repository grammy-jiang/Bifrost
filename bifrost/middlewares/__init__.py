"""
Base Middleware
"""
from asyncio.events import AbstractEventLoop
from typing import Any

from bifrost import signals
from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop


class BaseMiddleware:
    """
    Base Middleware
    """

    name = "base_middleware"

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        self.service = service
        self.settings = settings

        self._loop: AbstractEventLoop = get_event_loop(settings)

    @classmethod
    def from_service(cls, service: Service):
        """

        :param service:
        :type service: Service
        :return:
        :rtype:
        """
        settings: Settings = service.settings
        obj = cls(service, settings)

        service.signal_manager.connect(
            obj.service_started, signal=signals.service_started
        )
        service.signal_manager.connect(
            obj.service_stopped, signal=signals.service_stopped
        )

        return obj

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        raise NotImplementedError

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        raise NotImplementedError
