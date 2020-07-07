"""
Miscellaneous
"""
from importlib import import_module
from typing import Union


def load_object(path):
    """
    Load an object given its absolute object path, and return it.

    object can be the import path of a class, function, variable or an
    instance, e.g. "bifrost.service.bifrost.BifrostService"
    """
    module, name = path.rsplit(".", 1)
    mod = import_module(module)

    return getattr(mod, name)


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
    elif isinstance(text, str):
        return text
    raise TypeError


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
    elif isinstance(text, bytes):
        return text
    raise TypeError
