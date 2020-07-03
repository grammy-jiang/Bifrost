"""
Default settings
"""
import logging
from typing import Dict, Optional, Union

# ==== LOG CONFIGURATION ======================================================

LOG_LEVEL = logging.INFO
LOG_FORMATTER_FMT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_FORMATTER_DATEFMT = "%Y-%m-%d %H:%M:%S"

# ==== CORE MODULES ===========================================================

CLS_SERVICE = "bifrost.service.bifrost.Bifrost"

CLS_SIGNAL_MANAGER = "bifrost.signals.SignalManager"

CLS_EXTENSION_MANAGER = "bifrost.extensions.ExtensionManager"
CLS_MIDDLEWARE_MANAGER = "bifrost.middlewares.MiddlewareManager"

CLS_CHANNEL = "bifrost.channels.channel.Channel"

LOOP = "uvloop"

# ==== Extensions =============================================================

LOGSTATS_INTERVAL = 60  # in seconds

MAIL_SERVER: Optional[str] = None
MAIL_PORT: Optional[int] = None
MAIL_USERNAME: Optional[str] = None
MAIL_PASSWORD: Optional[str] = None
MAIL_FROM: Optional[str] = None
MAIL_TO: Optional[str] = None
MAIL_SUBJECT: Optional[str] = None
MAIL_CONTENT: Optional[str] = None

RPC_ADDRESS = "127.0.0.1:50051"
RPC_SERVER_CREDENTIALS_PRIVATE_KEYS: Optional[str] = None
RPC_SERVER_CREDENTIALS_CERTIFICATES: Optional[str] = None
RPC_SERVER_CREDENTIALS_CLIENT_AUTH: bool = False
RPC_STOP_GRACE: Optional[float] = None

WEB_ADDRESS = "127.0.0.1"
WEB_PORT = 8000
WEB_DEBUG = False

# Refer to:
# https://docs.python.org/3/library/ssl.html#ssl.create_default_context
# https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_cert_chain
WEB_SSL_CERT_FILE = None
WEB_SSL_KEY_FILE = None
WEB_SSL_PASSWORD = None

WEB_GRAPHQL_SCHEMA_QUERY = "bifrost.extensions.web.Query"
# WEB_GRAPHQL_SCHEMA_MUTATION = "bifrost.extensions.web.Mutation"
# WEB_GRAPHQL_SCHEMA_SUBSCRIPTION = "bifrost.extensions.web.Subscription"
# WEB_GRAPHQL_SCHEMA_DIRECTIVES = "bifrost.extensions.web.Directives"
# WEB_GRAPHQL_SCHEMA_TYPES = "bifrost.extensions.web.Types"

# ==== MODE ===================================================================

MIDDLEWARES: Dict[str, int] = {}

EXTENSIONS: Dict[str, int] = {
    "bifrost.extensions.LogStats": 0,
    "bifrost.extensions.Mail": 0,
    "bifrost.extensions.RPC": 0,
    "bifrost.extensions.Stats": 0,
    "bifrost.extensions.Web": 0,
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
        "INTERFACE_PROTOCOL": "bifrost.protocols.Interface",
        "INTERFACE_ADDRESS": "127.0.0.1",
        "INTERFACE_PORT": 1080,
        "CLIENT_PROTOCOL": "bifrost.protocols.Client",
        "CLIENT_ADDRESS": "127.0.0.1",
        "CLIENT_PORT": 1081,
        "CLIENT_SSL_CERT_FILE": None,
        "CLIENT_SSL_KEY_FILE": None,
        "CLIENT_SSL_PASSWORD": None,
    },
    # "server": {  # MODE: SERVER
    #     "INTERFACE_PROTOCOL": "bifrost.protocols.Socks5Protocol",
    #     "INTERFACE_ADDRESS": "127.0.0.1",
    #     "INTERFACE_PORT": 1080,
    #     "INTERFACE_SSL_CERT_FILE": None,
    #     "INTERFACE_SSL_KEY_FILE": None,
    #     "INTERFACE_SSL_PASSWORD": None,
    #     "CLIENT_PROTOCOL": "bifrost.protocols.Client",
    # }
}
