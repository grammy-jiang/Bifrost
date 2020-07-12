"""
Extension Manager
"""
import pprint
from typing import Dict

from bifrost.base import BaseComponent, LoggerMixin, ManagerMixin, SingletonMeta


class ExtensionManager(
    LoggerMixin, ManagerMixin, BaseComponent, metaclass=SingletonMeta
):
    """
    Extension Manager
    """

    manage = "EXTENSIONS"
    name = "ExtensionManager"
    setting_prefix = "EXTENSION_MANAGER_"

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name:
        :param setting_prefix:
        :type setting_prefix:
        """
        super(ExtensionManager, self).__init__(service, name, setting_prefix)

        self.logger.info(
            "Enabled extensions: \n%s", pprint.pformat(self.cls_extensions)
        )

    @property
    def cls_extensions(self) -> Dict[str, int]:
        """
        Get all extensions with the priority in a dict
        :return:
        :rtype: Dict[str, int]
        """
        return self._cls_components

    @property
    def extensions(self) -> Dict[str, object]:
        """
        Get all extensions by names in a dict
        :return:
        :rtype: Dict[str, object]
        """
        return self._components

    def get_extension(self, name: str) -> object:
        """
        Get an extension by its name
        :param name:
        :type name: str
        :return:
        :rtype: object
        """
        return self.extensions[name]
