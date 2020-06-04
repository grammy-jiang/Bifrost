"""
Base Extension Class
"""
from __future__ import annotations

from asyncio.events import AbstractEventLoop
from typing import TYPE_CHECKING, Any

from bifrost import signals
from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop

if TYPE_CHECKING:
    from bifrost.service import Service


class BaseExtension:
    """
    The base extension class
    """

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        self.service: Service = service
        self._loop: AbstractEventLoop = get_event_loop(settings)
        self.settings: Settings = settings

    @classmethod
    def from_service(cls, service: Service) -> BaseExtension:
        """

        :param service:
        :type service: Service
        :return:
        :rtype: BaseExtension
        """
        settings: Settings = service.settings
        obj = cls(service, settings)

        service.signal_manager.connect(obj.service_started, signal=signals.service_started)
        service.signal_manager.connect(obj.service_stopped, signal=signals.service_stopped)

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
