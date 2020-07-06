"""
Socks5 Protocol Mixin
"""


class Socks5Mixin:
    """
    Socks5 Protocol Mixin
    """

    def process_request(self, data: bytes) -> bytes:
        """

        :param data:
        :type data: bytes
        :return:
        :rtype: bytes
        """
