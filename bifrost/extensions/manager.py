"""
Extension Manager
"""
from __future__ import annotations

import logging
import pprint
from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings
from bifrost.utils.manager import Manager

logger = logging.getLogger(__name__)


class ExtensionManager(Manager):
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
        super(ExtensionManager, self).__init__(service, settings)

        self._register_components("EXTENSIONS")
        logger.info("Enabled extensions: \n%s", pprint.pformat(self.cls_components))
