"""
Stats Mixin
"""


class StatsMixin:  # pylint: disable=too-few-public-methods
    """
    Stats Mixin
    """

    @property
    def stats(self):
        """

        :return:
        :rtype:
        """
        return self.service.stats
