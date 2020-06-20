"""
Extension Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import TYPE_CHECKING

from bifrost.settings import Settings
from bifrost.utils.manager import Manager

if TYPE_CHECKING:
    from bifrost.service import Service

logger = logging.getLogger(__name__)


class ExtensionManager(Manager):
    """
    Extension Manager
    """

    def __init__(self, service: Service, settings: Settings):
        """

        :param service:
        :type service: Service
        :param settings:
        :type settings: Settings
        """
        super(ExtensionManager, self).__init__(service, settings)

        self._register_components("EXTENSIONS")
        logger.info("Enabled extensions: \n%s", pprint.pformat(self.cls_components))

    def get_extension(self, name: str) -> object:
        """
        get an extension by its name
        :param name:
        :type name: str
        :return:
        :rtype: object
        """
        return next(
            component
            for component in self.components
            if component.name.startswith(name)
        )
