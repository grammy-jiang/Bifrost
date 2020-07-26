"""
Signal Manager Mixin
"""
from functools import cached_property


class SignalManagerMixin:  # pylint: disable=too-few-public-methods
    """
    Signal Manager Mixin
    """

    @cached_property
    def signal_manager(self):
        """

        :return:
        :rtype:
        """
        if hasattr(self, "service"):
            return self.service.signal_manager
        elif hasattr(self, "channel"):
            return self.channel.signal_manager
        elif hasattr(self, "protocol"):
            return self.protocol.signal_manager
