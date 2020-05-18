"""
Default settings
"""
import logging

# ==== LOG CONFIGURATION ======================================================
from typing import Dict

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER_FMT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_FORMATTER_DATEFMT = "%Y-%m-%d %H:%M:%S"

# ==== CORE MODULES ===========================================================

SERVICE = "bifrost.service.bifrost.BifrostService"

MIDDLEWARE_MANAGER = "bifrost.middlewares.manager.MiddlewareManager"
EXTENSION_MANAGER = "bifrost.extensions.manager.ExtensionManager"

# ==== MODE ===================================================================

# the role that bifrost will play; it could be server or client
ROLE = "server"

MIDDLEWARES: Dict[str, int] = {}

EXTENSIONS: Dict[str, int] = {}
