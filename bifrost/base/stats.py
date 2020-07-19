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
        if service := getattr(self, "service"):
            return service.stats
