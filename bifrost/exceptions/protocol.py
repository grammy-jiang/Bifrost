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
    protocol not defined in transport or interface protocol
    """


class TransportNotDefinedException(BifrostException):
    """
    transport not defined for protocols
    """


class Socks5Exception(BifrostException):
    """
    base exception for Socks5 protocol
    """
