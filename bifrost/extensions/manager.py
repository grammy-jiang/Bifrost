"""
Extension Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import TYPE_CHECKING, Dict

from bifrost.utils.manager import Manager

if TYPE_CHECKING:
    from bifrost.service import Service
    from bifrost.settings import Settings

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
        logger.info("Enabled extensions: \n%s", pprint.pformat(self._cls_components))

    @property
    def extensions(self) -> Dict[str, object]:
        """
        get all extensions in a dict
        :return:
        :rtype: Dict[str, object]
        """
        return self._components

    def get_extension(self, name: str) -> object:
        """
        get an extension by its name
        :param name:
        :type name: str
        :return:
        :rtype: object
        """
        return self.extensions[name]
