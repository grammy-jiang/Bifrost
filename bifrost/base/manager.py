"""
Base Manager Class for extensions and middlewares
"""
from typing import Dict

from bifrost.base import BaseComponent
from bifrost.utils.misc import load_object


class BaseManager(BaseComponent):
    """
    Base Manager Class for extensions and middlewares
    """

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        super(BaseManager, self).__init__(service, name, setting_prefix)

        self._cls_components: Dict[str, int]
        self._components: Dict[str, object]

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
