"""
Create a singleton object for asyncio loop
"""
from asyncio.events import AbstractEventLoop
from typing import Optional

from bifrost.settings import Settings
from bifrost.utils.misc import load_object

# Never import __LOOP directly, use the following method get_event_loop instead
_LOOP: Optional[AbstractEventLoop] = None


def get_event_loop(  # pylint: disable=bad-continuation
    settings: Settings, func: str = "new_event_loop", **kwargs
) -> AbstractEventLoop:
    """
    Return a singleton object for asyncio loop
    :param settings:
    :type settings: Settings
    :param func:
    :type func: str
    :param kwargs:
    :return:
    :rtype: AbstractEventLoop
    """

    global _LOOP  # pylint: disable=global-statement

    if _LOOP is None:
        loop_path: str = ".".join([settings["LOOP"], func])
        _LOOP = load_object(loop_path)(**kwargs)

    return _LOOP
