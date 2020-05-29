from __future__ import annotations

from typing import Type

from bifrost.service import Service
from bifrost.settings import Settings


class BaseExtension:
    def __init__(self, service: Type[Service], settings: Settings):
        self.service: Type[Service] = service
        self.settings: Settings = settings

    @classmethod
    def from_service(cls, service: Type[Service]) -> BaseExtension:
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
        return obj

    def loop_started(self, sender):
        raise NotImplementedError

    def loop_stopped(self, sender):
        raise NotImplementedError
