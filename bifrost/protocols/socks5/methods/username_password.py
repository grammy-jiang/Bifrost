"""
RFC 1929 - Username/Password Authentication for SOCKS V5
https://datatracker.ietf.org/doc/rfc1929/
"""
from __future__ import annotations

from functools import cached_property
from struct import pack

from bifrost.base import LoggerMixin, SingletonMeta
from bifrost.exceptions.protocol import (
    ProtocolNotDefinedException,
    Socks5AuthenticationFailed,
)
from bifrost.utils.misc import load_object, to_str


class UsernamePasswordAuthConfigBackend:
    """
    A backend for username/password authentication through config
    """

    def __init__(self, auth: UsernamePasswordAuth):
        """

        :param auth:
        :type auth: UsernamePasswordAuth
        """
        self.auth = auth
        self.users = self.config["USERNAMEPASSWORD_USERS"]

    @classmethod
    def from_auth(cls, auth: UsernamePasswordAuth) -> UsernamePasswordAuthConfigBackend:
        """

        :param auth:
        :type auth: UsernamePasswordAuth
        :return:
        :rtype: UsernamePasswordAuthConfigBackend
        """
        obj = cls(auth)
        return obj

    @cached_property
    def config(self):
        """

        :return:
        """
        return self.auth.config

    def authenticate(self, username: bytes, password: bytes) -> bool:
        """

        :param username:
        :type username: bytes
        :param password:
        :type password: bytes
        :return:
        :rtype: bool
        """
        _username = to_str(username)
        _password = to_str(password)
        if _username in self.users and _password == self.users[_username]:
            return True
        return False


class UsernamePasswordAuthRDBackend:
    """
    A backend for username/password authentication through relational database
    """

    def __init__(self, auth: UsernamePasswordAuth):
        """

        :param auth:
        :type auth: UsernamePasswordAuth
        """
        self.auth = auth

    @classmethod
    def from_auth(cls, auth: UsernamePasswordAuth) -> UsernamePasswordAuthRDBackend:
        """

        :param auth:
        :type auth: UsernamePasswordAuth
        :return:
        :rtype: UsernamePasswordAuthRDBackend
        """
        obj = cls(auth)
        return obj

    @cached_property
    def config(self):
        """

        :return:
        """
        return self.auth.config

    def authenticate(self, username: bytes, password: bytes) -> bool:
        """

        :param username:
        :type username: bytes
        :param password:
        :type password: bytes
        :return:
        :rtype: bool
        """
        _username = to_str(username)
        _password = to_str(password)

        # TODO: verify the username


class UsernamePasswordAuth(LoggerMixin, metaclass=SingletonMeta):
    """
    Username/Password Authentication for SOCKS V5
    """

    value = 0x02
    next_state = "AUTH"

    def __init__(self):
        """

        """
        self._protocol = None
        self._backend = None

    @classmethod
    def from_protocol(cls, protocol) -> UsernamePasswordAuth:
        """

        :param protocol:
        :type protocol:
        :return:
        :rtype: UsernamePassword
        """
        obj = cls()
        obj.protocol = protocol

        return obj

    @property
    def protocol(self):
        """

        :return:
        """
        if not self._protocol:
            raise ProtocolNotDefinedException()
        return self._protocol

    @protocol.setter
    def protocol(self, value) -> None:
        """

        :param value:
        :return:
        :rtype: None
        """
        self._protocol = value

    @property
    def config(self):
        """

        :return:
        """
        return self.protocol.config

    @property
    def backend(self):
        """

        :return:
        """
        if not self._backend:
            cls_backend = load_object(self.config["USERNAMEPASSWORD_AUTH_BACKEND"])
            self._backend = cls_backend.from_auth(self)
        return self._backend

    def auth(self, data: bytes) -> None:
        """

        :param data:
        :type data:
        :return:
        :rtype: None
        """
        ver: int = data[0]
        ulen: int = data[1]
        uname: bytes = data[2 : 2 + ulen]
        plen: int = data[2 + ulen]
        passwd: bytes = data[2 + ulen + 1 : 2 + ulen + 1 + plen]

        if self.backend.authenticate(uname, passwd):
            self.protocol.transport.write(pack("!BB", ver, 0x00))
        else:
            self.protocol.transport.write(pack("!BB", ver, 0xFF))
            self.logger.info("Authentication failed: [%s]", to_str(uname))
            raise Socks5AuthenticationFailed
