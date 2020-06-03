"""
Create a singleton object for asyncio loop
"""
from asyncio.events import AbstractEventLoop
from typing import Optional, Type

from bifrost.settings import Settings
from bifrost.utils.misc import load_object

__loop: Optional[Type[AbstractEventLoop]] = None


def get_event_loop(
    settings: Settings, func: str = "new_event_loop", *args, **kwargs
) -> Type[AbstractEventLoop]:
    """
    Return a singleton object for asyncio loop
    :param settings:
    :type settings: Settings
    :param func:
    :type func: str
    :param args:
    :param kwargs:
    :return:
    :rtype: Type[AbstractEventLoop]
    """

    global __loop

    if __loop is None:
        loop_path: str = ".".join([settings["LOOP"], func])
        __loop = load_object(loop_path)(*args, **kwargs)

    return __loop
