"""
Stats Mixin
"""


class StatsMixin:
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
