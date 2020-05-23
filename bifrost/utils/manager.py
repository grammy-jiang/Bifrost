from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Type

from bifrost.settings import Settings
from bifrost.utils.misc import load_object

if TYPE_CHECKING:
    from bifrost.service import Service


class Manager:
    def __init__(self, service: Type["Service"], settings: Settings):
        """

        :param service:
        :type service: Type["Service"]
        :param settings:
        :type settings: Settings
        """
        self.service: Type["Service"] = service
        self.settings: Settings = settings

        self.cls_components: Optional[Dict[str, int]] = None
        self.components: Optional[List] = None

    @classmethod
    def from_service(cls, service: Type["Service"]) -> Manager:
        """

        :param service:
        :type service: Type["Service"]
        :return:
        :rtype: Manager
        """
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
        return obj

    def _register_components(self, key: str) -> None:
        """

        :param key: the setting name in Settings
        :return:
        :rtype: None
        """
        self.cls_components = dict(
            sorted(self.settings[key].items(), key=lambda items: items[1])
        )
        self.components = [
            load_object(cls).from_service(self.service)
            for cls in self.cls_components.keys()
        ]
