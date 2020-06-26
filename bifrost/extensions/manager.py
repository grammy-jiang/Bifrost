"""
Extension Manager
"""
import logging
import pprint
from typing import TYPE_CHECKING, Dict

from bifrost.base import BaseManager

if TYPE_CHECKING:
    from bifrost.service import Service

logger = logging.getLogger(__name__)


class ExtensionManager(BaseManager):
    """
    Extension Manager
    """

    name = "Extension Manager"
    setting_prefix = "EXTENSION_MANAGER_"

    def __init__(self, service: Service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service: Service
        """
        super(ExtensionManager, self).__init__(service, name, setting_prefix)

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
