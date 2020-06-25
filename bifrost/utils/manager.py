"""
Base Manager Class for extensions and middlewares
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from bifrost.signals import service_started, service_stopped
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.settings import Settings


class Manager:
    """
    Base Manager Class for extensions and middlewares
    """

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        self.service: Service = service
        self.settings: Settings = settings

        self._cls_components: Dict[str, int]
        self._components: Dict[str, object]

    @classmethod
    def from_service(cls, service: Service) -> Manager:
        """

        :param service:
        :type service: Service
        :return:
        :rtype: Manager
        """
        settings: Settings = service.settings
        obj = cls(service, settings)

        service.signal_manager.connect(obj.service_started, service_started)
        service.signal_manager.connect(obj.service_stopped, service_stopped)
        return obj

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """

    def _register_components(self, key: str) -> None:
        """

        :param key: the setting name in Settings
        :return:
        :rtype: None
        """
        self._cls_components = dict(
            sorted(self.settings[key].items(), key=lambda items: items[1])
        )

        self._components = {
            cls.name: cls.from_service(self.service)
            for cls in (load_object(cls) for cls in self._cls_components.keys())
        }
