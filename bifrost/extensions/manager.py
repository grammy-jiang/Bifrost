"""
Extension Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.misc import load_object

logger = logging.getLogger(__name__)


class ExtensionManager:
    """
    Extension Manager
    """

    def __init__(self, service: Type[Service], settings: Settings):
        """

        :param service:
        :type service: Type[Service]
        :param settings:
        :type settings: Settings
        """
        self.service = service
        self.settings = settings

        self.cls_extensions = dict(
            sorted(self.settings["EXTENSIONS"].items(), key=lambda items: items[1])
        )
        self.obj_extensions = [
            load_object(cls).from_service(self.service)
            for cls in self.cls_extensions.keys()
        ]
        logger.info("Enabled extensions: \n%s", pprint.pformat(self.cls_extensions))

    @classmethod
    def from_service(cls, service: Type[Service]) -> ExtensionManager:
        """

        :param service:
        :type service: Type[Service]
        :return:
        :rtype: ExtensionManager
        """
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
        return obj
