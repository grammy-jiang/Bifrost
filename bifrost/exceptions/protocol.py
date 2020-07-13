"""
Exceptions used in Protocols
"""
from bifrost.exceptions import BifrostException


class ProtocolVersionNotSupportedException(BifrostException):
    """
    The protocol version is not supported
    """


class ProtocolNotDefinedException(BifrostException):
    """

    """


class TransportNotDefinedException(BifrostException):
    """

    """
