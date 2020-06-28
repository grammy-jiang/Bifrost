"""
Signal Manager (Dispatcher)
"""
from __future__ import annotations

import asyncio
import functools
from asyncio.events import AbstractEventLoop
from collections import defaultdict
from typing import Callable, Dict, Set

from bifrost.base import LoggerMixin
from bifrost.settings import Settings
from bifrost.utils.loop import get_event_loop


class SignalManager(LoggerMixin):
    """
    Signal Manager
    """

    def __init__(self, settings: Settings):
        """

        :param settings:
        :type settings: Settings
        """
        self.settings: Settings = settings

        self._loop: AbstractEventLoop = get_event_loop(settings)

        self._all: Dict[object, Set[Callable]] = defaultdict(set)

    @classmethod
    def from_settings(cls, settings: Settings) -> SignalManager:
        """

        :param settings:
        :type settings: Settings
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
        self._all[signal].add(receiver)

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
            self._all[signal].remove(receiver)
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
        receivers: Set[Callable] = self._all[signal]

        receiver: Callable
        for receiver in receivers:
            _receiver = functools.partial(receiver, **kwargs)
            if asyncio.iscoroutinefunction(receiver):
                self._loop.create_task(_receiver())
            else:
                self._loop.call_soon_threadsafe(_receiver)
