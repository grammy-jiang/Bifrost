"""
Signal Manager (Dispatcher)
"""
from __future__ import annotations

import asyncio
import functools
from collections import UserDict
from typing import Callable, Set

from bifrost.base import LoggerMixin
from bifrost.utils.loop import get_event_loop


class SignalManager(UserDict, LoggerMixin):
    """
    Signal Manager
    """

    def __init__(self, settings):
        """

        :param settings:
        :type settings:
        """
        super(SignalManager, self).__init__()

        self.settings = settings

        self._loop = get_event_loop(settings)

    def __missing__(self, key):
        self[key] = set()
        return self[key]

    @classmethod
    def from_settings(cls, settings) -> SignalManager:
        """

        :param settings:
        :type settings:
        :return:
        :rtype: SignalManager
        """
        obj = cls(settings)
        return obj

    def connect(self, receiver: Callable, signal: object) -> None:
        """
        Connect a receiver function to a signal.

        :param receiver: the function to be connected
        :type receiver: callable
        :param signal: the signal to connect to
        :type signal: object
        :return:
        :rtype: None
        """
        self[signal].add(receiver)

    def disconnect(self, receiver: Callable, signal: object) -> None:
        """
        Disconnect a receiver function from a signal. This has the opposite
        effect of the connect method, and the arguments are the same.

        :param receiver:
        :type receiver: Callable
        :param signal:
        :type signal: object
        :return:
        :rtype: None
        """
        try:
            self[signal].remove(receiver)
        except KeyError as exc:
            self.logger.exception(exc)

    def send(self, signal: object, **kwargs) -> None:
        """
        Send a signal, catch exceptions and log them.

        The keyword arguments are passed to the signal handlers (connected
        through the connect method).

        :param signal:
        :type signal: object
        :param kwargs:
        :return:
        :rtype: None
        """
        receivers: Set[Callable] = self[signal]

        receiver: Callable
        for receiver in receivers:
            _receiver = functools.partial(receiver, **kwargs)
            if asyncio.iscoroutinefunction(receiver):
                self._loop.create_task(_receiver())
            else:
                self._loop.call_soon_threadsafe(_receiver)
