"""
Logger Mixin
"""
import logging


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """
    Logger Mixin
    """

    @property
    def logger(self) -> logging.Logger:
        """
        Logger
        :return:
        :rtype: Logger
        """
        name = ".".join([self.__module__, self.__class__.__name__])
        return logging.getLogger(name)
