from __future__ import annotations

import asyncio
from asyncio.events import AbstractEventLoop
from typing import Callable, Type

from bifrost.service import Service
from bifrost.settings import Settings


class SignalManager:
    def __init__(self, service, settings, loop=None):
        self.service: Type[Service] = service
        self.settings: Settings = settings
        self._loop: Type[AbstractEventLoop] = loop if loop else asyncio.get_event_loop()

    @classmethod
    def from_service(cls, service) -> SignalManager:
        loop: Type[AbstractEventLoop] = getattr(service, "loop")
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings, loop)
        return obj

    def connect(self, receiver: Callable, signal: object):
        """
        Connect a receiver function to a signal.

        :param receiver: the function to be connected
        :type receiver: callable

        :param signal: the signal to connect to
        :type signal: object
        """

    def disconnect(self, receiver: Callable, signal: object):
        """
        Disconnect a receiver function from a signal. This has the opposite
        effect of the connect method, and the arguments are the same.
        """

    def send(self, signal: object, **kwargs):
        """
        Send a signal, catch exceptions and log them.

        The keyword arguments are passed to the signal handlers (connected
        through the connect method).
        """

    def disconnect_all(self, signal: object, **kwargs):
        """
        Disconnect all receivers from the given signal.

        :param signal: the signal to disconnect from
        :type signal: object
        """
