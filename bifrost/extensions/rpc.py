"""
RPC

Refer to:
* https://grpc.io/
* https://grpc.github.io/grpc/python/index.html
"""
from __future__ import annotations

import logging
from typing import Any

from bifrost.extensions import BaseExtension

logger = logging.getLogger(__name__)


class RPC(BaseExtension):
    """
    RPC
    """

    name = "RPC"
    setting_prefix = "RPC_"

    def service_started(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        super(RPC, self).service_started(sender)
        logger.info("Extension [%s] is running...", self.name)

    def service_stopped(self, sender: Any) -> None:
        """

        :param sender:
        :type sender: Any
        :return:
        :rtype: None
        """
        logger.info("Extension [%s] is stopped.", self.name)
