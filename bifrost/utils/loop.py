"""
Create a singleton object for asyncio loop
"""
from asyncio.events import AbstractEventLoop
from typing import Optional, Type

from bifrost.settings import Settings
from bifrost.utils.misc import load_object

# Never import __LOOP directly, use the following method get_event_loop instead
__LOOP: Optional[Type[AbstractEventLoop]] = None


def get_event_loop(  # pylint: disable=bad-continuation
    settings: Settings, func: str = "new_event_loop", **kwargs
) -> Type[AbstractEventLoop]:
    """
    Return a singleton object for asyncio loop
    :param settings:
    :type settings: Settings
    :param func:
    :type func: str
    :param kwargs:
    :return:
    :rtype: Type[AbstractEventLoop]
    """

    global __LOOP  # pylint: disable=global-statement

    if __LOOP is None:
        loop_path: str = ".".join([settings["LOOP"], func])
        __LOOP = load_object(loop_path)(**kwargs)

    return __LOOP
