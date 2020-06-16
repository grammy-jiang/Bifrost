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

CLS_SERVICE = "bifrost.service.bifrost.Bifrost"

CLS_SIGNAL_MANAGER = "bifrost.signals.manager.SignalManager"

CLS_EXTENSION_MANAGER = "bifrost.extensions.manager.ExtensionManager"
CLS_MIDDLEWARE_MANAGER = "bifrost.middlewares.manager.MiddlewareManager"

CLS_CHANNEL = "bifrost.channels.channel.Channel"

LOOP = "uvloop"

# ==== Extensions =============================================================

LOGSTATS_INTERVAL = 60  # in seconds

WEB_ADDRESS = "127.0.0.1"
WEB_PORT = 8000

# ==== MODE ===================================================================

MIDDLEWARES: Dict[str, int] = {}

EXTENSIONS: Dict[str, int] = {
    "bifrost.extensions.logstats.LogStats": 0,
    "bifrost.extensions.web.Web": 0,
}

# ==== CHANNELS ===============================================================

"""
-----------     =============                 =============      -----------
| YOUR    | - > | INTERFACE |      GREAT      | CLIENT    | - >  | TARGET  |
| MACHINE |     | CLIENT    | - > FIREWALL - >| INTERFACE |      | WEBSITE |
-----------     =============                 =============      -----------
               (BIFROST CLIENT)              (BIFROST SERVER)
"""

CHANNELS: Dict[str, Dict[str, Union[str, int]]] = {
    "client": {  # MODE: CLIENT
        "INTERFACE_PROTOCOL": "bifrost.protocols.client.Interface",
        "INTERFACE_ADDRESS": "127.0.0.1",
        "INTERFACE_PORT": 1080,
        "CLIENT_PROTOCOL": "bifrost.protocols.client.Client",
        "CLIENT_PROTOCOL_ADDRESS": "127.0.0.1",
        "CLIENT_PROTOCOL_PORT": 1081,
    },
    # "server": {  # MODE: SERVER
    #     "INTERFACE_PROTOCOL": "bifrost.protocols.server.Interface"
    #     "INTERFACE_ADDRESS": "127.0.0.1",
    #     "INTERFACE_PORT": 1081,
    #     "CLIENT_PROTOCOL": "bifrost.protocols.server.Client",
    # }
}
