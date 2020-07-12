"""
Metaclass for Singleton
"""
from typing import Dict, Type


class SingletonMeta(type):
    """
    Metaclass for Singleton
    """

    _instances: Dict[Type, object] = {}

    def __call__(cls, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances.update({cls: instance})
        return cls._instances[cls]
