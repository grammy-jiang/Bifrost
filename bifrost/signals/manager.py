from __future__ import annotations

import asyncio
import functools
import logging
from asyncio.events import AbstractEventLoop
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, Set, Type

from bifrost.settings import Settings

if TYPE_CHECKING:
    from bifrost.service import Service

logger = logging.getLogger(__name__)


class SignalManager:
    def __init__(self, service, settings):
        self.service: Type[Service] = service
        self.settings: Settings = settings
        self._loop: Type[AbstractEventLoop] = service.loop

        self._all: Dict[object, Set[Callable]] = defaultdict(set)

    @classmethod
    def from_service(cls, service: Type[Service]) -> SignalManager:
        """

        :param service:
        :type service: Type[Service]
        :return:
        """
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
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
            logger.exception(exc)

    def send(self, signal: object, **kwargs):
        """
        Send a signal, catch exceptions and log them.

        The keyword arguments are passed to the signal handlers (connected
        through the connect method).

        :param signal:
        :type signal: object
        """
        receivers: Set[Callable] = self._all[signal]

        receiver: Callable
        for receiver in receivers:
            _receiver = functools.partial(receiver, **kwargs)
            if asyncio.iscoroutinefunction(receiver):
                self._loop.create_task(_receiver())
            else:
                self._loop.call_soon_threadsafe(_receiver)
