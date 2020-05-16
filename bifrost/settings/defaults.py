"""
Default settings
"""
import logging

# ==== LOG CONFIGURATION ======================================================

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER_FMT = "%(asctime)-15s [%(name)s] %(levelname)-8s: %(message)s"
LOG_FORMATTER_DATEFMT = "%Y-%m-%d %H:%M:%S"

# ==== MODE ===================================================================

# the role that bifrost will play; it could be server or client
ROLE = "server"
