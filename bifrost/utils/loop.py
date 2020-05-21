from asyncio.events import AbstractEventLoop
from typing import Type

from bifrost.settings import Settings
from bifrost.utils.misc import load_object

_loop = None


def get_event_loop(
    settings: Settings, func: str = "new_event_loop"
) -> Type[AbstractEventLoop]:
    """

    :return:
    :rtype: Type[BaseEventLoop]
    """
    global _loop
    if _loop is None:
        loop_path: str = ".".join([settings["LOOP"], func])
        _loop = load_object(loop_path)
        return _loop()
    else:
        return _loop
