"""
Stats Mixin
"""
from functools import cached_property


class StatsMixin:  # pylint: disable=too-few-public-methods
    """
    Stats Mixin
    """

    @cached_property
    def stats(self):
        """

        :return:
        :rtype:
        """
        if hasattr(self, "service"):
            return self.service.stats
        elif hasattr(self, "extension_manager"):
            return self.extension_manager.get_extension(name="Stats")
