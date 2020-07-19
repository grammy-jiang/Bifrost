"""
Logger Mixin
"""
import logging
from functools import cached_property


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """
    Logger Mixin
    """

    @cached_property
    def logger(self) -> logging.Logger:
        """
        Logger
        :return:
        :rtype: Logger
        """
        name = ".".join([self.__module__, self.__class__.__name__])
        return logging.getLogger(name)
