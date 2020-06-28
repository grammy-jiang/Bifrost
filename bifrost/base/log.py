"""
Logger Mixin
"""
import logging


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """
    Logger Mixin
    """

    @property
    def logger(self):
        """
        Logger
        :return:
        """
        name = ".".join([self.__module__, self.__class__.__name__])
        return logging.getLogger(name)
