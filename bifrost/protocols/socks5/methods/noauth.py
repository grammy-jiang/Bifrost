"""
No Authentication for Socks5
"""
from bifrost.protocols.socks5 import HOST


class NoAuth:
    """
    No Authentication for Socks5
    """

    value = 0x00
    transit_to = HOST
