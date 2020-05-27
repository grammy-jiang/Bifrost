"""
Default settings
"""
import logging
from typing import Dict, Union

# ==== LOG CONFIGURATION ======================================================

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER_FMT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_FORMATTER_DATEFMT = "%Y-%m-%d %H:%M:%S"

# ==== CORE MODULES ===========================================================

SERVICE = "bifrost.service.bifrost.BifrostService"

SIGNAL_MANAGER = "bifrost.signals.manager.SignalManager"

MIDDLEWARE_MANAGER = "bifrost.middlewares.manager.MiddlewareManager"
EXTENSION_MANAGER = "bifrost.extensions.manager.ExtensionManager"

LOOP = "asyncio"

# ==== MODE ===================================================================

# the role that bifrost will play; it could be server or client
ROLE = "client"

MIDDLEWARES: Dict[str, int] = {}

EXTENSIONS: Dict[str, int] = {}

# ==== MODE: CLIENT ===========================================================

CHANNELS: Dict[str, Dict[str, Union[str, int]]] = {
    "socks5": {
        "INTERFACE_PROTOCOL": "bifrost.protocols.socks5.Socks5Protocol",
        "INTERFACE_ADDRESS": "127.0.0.1",
        "INTERFACE_PORT": 1080,
    },
}
