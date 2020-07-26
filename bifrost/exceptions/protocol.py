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


class Socks5CMDNotSupportedException(Socks5Exception):
    """
    CMD is not supported other than:
    * CONNECT X'01'
    * BIND X'02'
    * UDP ASSOCIATE X'03'
    """


class Socks5NoAcceptableMethodsException(Socks5Exception):
    """
    No acceptable methods found for authentication
    """


class Socks5AuthenticationFailed(Socks5Exception):
    """
    Authentication failed
    """


class Socks5NetworkUnreachableException(Socks5Exception):
    """
    The target can't be reached
    """
