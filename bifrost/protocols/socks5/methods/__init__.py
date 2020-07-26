"""
The methods for authentications in Socks5
"""
from bifrost.protocols.socks5.methods.noauth import NoAuth
from bifrost.protocols.socks5.methods.username_password import (
    UsernamePasswordAuth,
    UsernamePasswordAuthConfigBackend,
    UsernamePasswordAuthSQLiteBackend,
)

__all__ = ["NoAuth", "UsernamePasswordAuth"]
