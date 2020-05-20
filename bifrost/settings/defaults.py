"""
Default settings
"""
import logging
from typing import Dict

# ==== LOG CONFIGURATION ======================================================

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER_FMT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_FORMATTER_DATEFMT = "%Y-%m-%d %H:%M:%S"

# ==== CORE MODULES ===========================================================

SERVICE = "bifrost.service.bifrost.BifrostService"

MIDDLEWARE_MANAGER = "bifrost.middlewares.manager.MiddlewareManager"
EXTENSION_MANAGER = "bifrost.extensions.manager.ExtensionManager"

LOOP = "asyncio"

# ==== MODE ===================================================================

# the role that bifrost will play; it could be server or client
ROLE = "server"

MIDDLEWARES: Dict[str, int] = {}

EXTENSIONS: Dict[str, int] = {}

# ==== MODE: CLIENT ===========================================================

CLIENT_PROTOCOLS = [
    {
        "protocol": "bifrost.protocols.socks5.Socks5Protocol",
        "host": "127.0.0.1",
        "port": 1080,
    },
    # {
    #     "protocol": "bifrost.protocols.http.HttpProtocol",
    #     "host": "127.0.0.1",
    #     "port": 80,
    # },
    # {
    #     "protocol": "bifrost.protocols.https.HttpsProtocol",
    #     "host": "127.0.0.1",
    #     "port": 443,
    # },
]
