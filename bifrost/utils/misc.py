"""
Miscellaneous
"""
import asyncio
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Union

from cachetools.func import lru_cache


@lru_cache
def load_object(path: str) -> Any:
    """
    Load an object given its absolute object path, and return it.

    object can be the import path of a class, function, variable or an
    instance, e.g. "bifrost.service.bifrost.BifrostService"

    :param path:
    :type path: str
    :return:
    :rtype: Any
    """
    module: str
    name: str
    module, name = path.rsplit(".", 1)
    mod: ModuleType = import_module(module)

    return getattr(mod, name)


@lru_cache
def to_str(text: Union[bytes, str], encoding="utf-8", errors="strict") -> str:
    """
    Convert text to str.

    Refer to:
    https://docs.python.org/3/library/stdtypes.html#bytes.decode

    :param text:
    :type text: Union[bytes, str]
    :param encoding:
    :type encoding: str
    :param errors:
    :type errors: str
    :return:
    :rtype: str
    """
    if isinstance(text, bytes):
        return text.decode(encoding, errors)
    if isinstance(text, str):
        return text
    raise TypeError


@lru_cache
def to_bytes(text: Union[bytes, str], encoding="utf-8", errors="strict") -> bytes:
    """
    Convert text to bytes.

    Refer to:
    https://docs.python.org/3/library/stdtypes.html#str.encode

    :param text:
    :type text: Union[bytes, str]
    :param encoding:
    :type encoding: str
    :param errors:
    :type errors: str
    :return:
    :rtype: bytes
    """
    if isinstance(text, str):
        return text.encode(encoding, errors)
    if isinstance(text, bytes):
        return text
    raise TypeError


def to_sync(func: Callable) -> Callable:
    """
    A decorator to convert function to sync
    :param func:
    :type func: Callable
    :return:
    :rtype: Callable
    """
    loop = asyncio.get_event_loop()

    def convert_to_sync(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return loop.run_until_complete(func(*args, **kwargs))
        else:
            return func(*args, **kwargs)

    return convert_to_sync
