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

CLS_SERVICE = "bifrost.service.bifrost.BifrostService"

CLS_SIGNAL_MANAGER = "bifrost.signals.manager.SignalManager"

CLS_EXTENSION_MANAGER = "bifrost.extensions.manager.ExtensionManager"
CLS_MIDDLEWARE_MANAGER = "bifrost.middlewares.manager.MiddlewareManager"

CLS_CHANNEL = "bifrost.channels.channel.Channel"

LOOP = "asyncio"

# ==== Extensions =============================================================

LOGSTATS_INTERVAL = 60  # in seconds

# ==== MODE ===================================================================

MIDDLEWARES: Dict[str, int] = {}

EXTENSIONS: Dict[str, int] = {
    "bifrost.extensions.logstats.LogStats": 0
}

# ==== MODE: CLIENT ===========================================================

CHANNELS: Dict[str, Dict[str, Union[str, int]]] = {
    "socks5": {
        "INTERFACE_PROTOCOL": "bifrost.protocols.socks5.Socks5Protocol",
        "INTERFACE_ADDRESS": "127.0.0.1",
        "INTERFACE_PORT": 1080,
    },
}
