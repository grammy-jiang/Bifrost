"""
Base Manager Class for extensions and middlewares
"""
from typing import Dict

from bifrost.utils.misc import load_object


class ManagerMixin:  # pylint: disable=too-few-public-methods
    """
    Base Manager Class for extensions and middlewares
    """

    manage: str = None  # type: ignore

    def __init__(self, service, name: str = None, setting_prefix: str = None):
        """

        :param service:
        :type service:
        :param name:
        :type name: str
        :param setting_prefix:
        :type setting_prefix: str
        """
        super().__init__(service, name, setting_prefix)  # type: ignore

        self._cls_components: Dict[str, int] = dict(
            sorted(
                self.settings[self.manage].items(),  # type: ignore
                key=lambda items: items[1],
            )
        )

        self._components: Dict[str, object] = {
            cls.name: cls.from_service(self.service)  # type: ignore
            for cls in (load_object(cls) for cls in self._cls_components.keys())
        }
