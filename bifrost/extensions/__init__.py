from __future__ import annotations

from asyncio.events import AbstractEventLoop
from typing import Type

from bifrost import signals
from bifrost.service import Service
from bifrost.settings import Settings


class BaseExtension:
    def __init__(self, service: Type[Service], settings: Settings):
        self.service: Type[Service] = service
        self.loop: Type[AbstractEventLoop] = service.loop
        self.settings: Settings = settings

    @classmethod
    def from_service(cls, service: Type[Service]) -> BaseExtension:
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)

        service.signal_manager.connect(obj.loop_started, signal=signals.loop_started)
        service.signal_manager.connect(obj.loop_stopped, signal=signals.loop_stopped)

        return obj

    def loop_started(self, sender):
        raise NotImplementedError

    def loop_stopped(self, sender):
        raise NotImplementedError
