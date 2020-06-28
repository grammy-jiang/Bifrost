"""
All ready to use extensions
"""
from bifrost.extensions.logstats import LogStats
from bifrost.extensions.mail import Mail
from bifrost.extensions.manager import ExtensionManager
from bifrost.extensions.rpc import RPC
from bifrost.extensions.stats import Stats
from bifrost.extensions.web import Web

__all__ = ["LogStats", "Mail", "ExtensionManager", "RPC", "Stats", "Web"]
