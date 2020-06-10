"""
Define Settings class
"""
from __future__ import annotations

import logging
from collections import namedtuple
from collections.abc import Mapping, MutableMapping
from contextlib import contextmanager
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, Generator, Union

from bifrost.exceptions.settings import (
    SettingsFrozenException,
    SettingsLowPriorityException,
)

# The pair of priority and priority_value
PRIORITIES: Dict[str, int] = {
    "default": 0,
    "user": 10,
    "project": 20,
    "env": 30,
    "cmd": 40,
}

logger = logging.getLogger(__name__)  # pylint: disable = invalid-name

Setting = namedtuple("Setting", ["priority", "priority_value", "value"])


class BaseSettings(MutableMapping):
    """
    The base class of Settings
    """

    class FrozenCheck:  # pylint: disable = too-few-public-methods
        """
        A decorator for Settings frozen status check
        """

        def __call__(self, method):
            def frozen_check(settings: BaseSettings, *args, **kwargs):
                if settings.is_frozen():
                    raise SettingsFrozenException
                return method(settings, *args, **kwargs)

            return frozen_check

    frozen_check = FrozenCheck()

    def __init__(self, settings: Mapping = None, priority: str = "project"):
        """

        :param settings:
        :type settings: Mapping
        :param priority:
        :type priority: str
        """
        self._data: Dict[str, Setting] = {}
        self._frozen: bool = False
        self._priority = priority
        if settings:
            self.update(settings)

        self._frozen = True

    def is_frozen(self) -> bool:
        """
        check this settings class frozen or not
        :return:
        """
        return self._frozen

    @contextmanager
    def unfreeze(  # pylint: disable = bad-continuation
        self, priority: str = "project"
    ) -> Generator:
        """
        A context manager to unfreeze this instance and keep the previous frozen
        status
        """
        _priority: str
        _priority, self._priority = self._priority, priority
        status: bool
        status, self._frozen = self._frozen, False
        try:
            yield self
        finally:
            self._priority = _priority
            self._frozen = status

    def update(  # pylint: disable = arguments-differ
        self, m: Mapping = None, **kwargs  # pylint: disable = bad-continuation
    ) -> None:
        """
        Update this instance with the given values
        :param m:
        :type m: Mapping
        :param kwargs:
        :type kwargs:
        :return
        :rtype: None
        """
        if m:
            for key, value in m.items():
                self[key] = value

        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    # ---- abstract methods of MutableMapping ---------------------------------

    def __getitem__(self, k: str) -> Any:
        """

        :param k:
        :type k: str
        :return:
        :rtype: Any
        """
        return self._data[k].value

    @frozen_check
    def __setitem__(self, k: str, v: Any) -> None:
        """

        :param k:
        :type k: str
        :param v:
        :type v: Any
        :return:
        :rtype: None
        """
        setting: Setting = Setting(
            priority=self._priority, priority_value=PRIORITIES[self._priority], value=v
        )
        if k in self:
            _v = self._data[k]
            if PRIORITIES[self._priority] < _v.priority_value:
                raise SettingsLowPriorityException

        self._data[k] = setting

    @frozen_check
    def __delitem__(self, k: str) -> None:
        """

        :param k:
        :type k: str
        :return:
        :rtype: None
        """
        del self._data[k]

    def __iter__(self):
        """

        :return:
        """
        return iter(self._data)

    def __len__(self) -> int:
        """

        :return:
        :rtype: int
        """
        return len(self._data)

    def __contains__(self, k: object) -> bool:
        """

        :return:
        :rtype: bool
        """
        return k in self._data


class Settings(BaseSettings):  # pylint: disable = too-many-ancestors
    """
    Settings class
    """

    def update_from_module(self, module: Union[str, ModuleType]) -> None:
        """
        update settings from a module
        :param module:
        :type module:
        :return:
        """
        if isinstance(module, str):
            module = import_module(module)

        for key in dir(module):
            if key.isupper():
                self[key] = getattr(module, key)
