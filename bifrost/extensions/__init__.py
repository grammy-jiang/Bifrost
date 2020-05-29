from __future__ import annotations

from bifrost.service import Service
from bifrost.settings import Settings


class BaseExtension:
    def __init__(self, service: Service, settings: Settings):
        self.service: Service = service
        self.settings: Settings = settings

    @classmethod
    def from_service(cls, service: Service) -> BaseExtension:
        settings: Settings = getattr(service, "settings")
        obj = cls(service, settings)
        return obj

    def loop_started(self):
        raise NotImplementedError

    def loop_stopped(self):
        raise NotImplementedError
