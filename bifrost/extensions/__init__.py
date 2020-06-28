"""
Base Extension Class
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Coroutine, Dict, Optional

from bifrost import signals
from bifrost.extensions.stats import Stats
from bifrost.settings import Settings

if TYPE_CHECKING:
    from bifrost.service import Service


class BaseExtension:
    """
    The base extension class
    """

    name = "base_extension"
    setting_prefix: Optional[str] = None

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        self.service: Service = service
        self.settings: Settings = settings

        self.config: Dict[str, Any] = {}
        for key, value in settings.items():
            if key.startswith(self.setting_prefix):
                self.config[key.replace(self.setting_prefix, "")] = value

        self.stats: Stats

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

    def service_started(  # pylint: disable=bad-continuation,unused-argument
        self, sender: Any
    ) -> Optional[Coroutine]:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        self.stats = self.service.stats

    def service_stopped(self, sender: Any) -> Optional[Coroutine]:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        raise NotImplementedError
