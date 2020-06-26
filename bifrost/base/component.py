"""
Base class for components
"""
from typing import Any, Dict

from bifrost.signals import service_started, service_stopped


class BaseComponent:
    """
    Base class for components, including:
    * manager
    * middleware
    * extension
    * channel
    """

    name: str = None  # type: ignore
    setting_prefix: str = None  # type: ignore

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name: str
        :param setting_prefix
        :type setting_prefix: str
        """
        self.service = service
        self.settings = service.settings

        if name:
            self.name = name

        if setting_prefix:
            self.setting_prefix = setting_prefix

        self.config: Dict[str, Any] = {
            key.replace(self.setting_prefix, ""): value
            for key, value in self.settings.items()
            if key.startswith(self.setting_prefix)
        }

    @classmethod
    def from_service(cls, service, name: str = None, setting_prefix: str = None):
        """
        Initialize components from a service instance
        :param service:
        :type service:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        :return:
        """
        obj = cls(service, name, setting_prefix)

        signal_manager = service.signal_manager
        signal_manager.connect(obj.service_started, service_started)
        signal_manager.connect(obj.service_stopped, service_stopped)

        return obj

    async def service_started(  # pylint: disable=bad-continuation,unused-argument
        self, sender: Any
    ) -> None:
        """
        Do some work when signal service_started send
        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        await self.start()

    async def service_stopped(  # pylint: disable=bad-continuation,unused-argument
        self, sender: Any
    ) -> None:
        """
        Do some work when signal service_stopped send
        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        await self.stop()

    async def start(self) -> None:
        """
        Start this component
        :return:
        :rtype: None
        """

    async def stop(self) -> None:
        """
        Stop this component
        :return:
        :rtype: None
        """
