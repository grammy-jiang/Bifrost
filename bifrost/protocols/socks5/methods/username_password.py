from __future__ import annotations

from struct import pack

from bifrost.exceptions.protocol import ProtocolNotDefinedException
from bifrost.protocols.socks5 import AUTH, HOST
from bifrost.utils.misc import load_object, to_str

_username_password_auth = None


class UsernamePasswordAuthConfigBackend:
    def __init__(self, auth):
        """

        :param auth:
        """
        self.auth = auth
        self.users = self.config["USERNAMEPASSWORD_USERS"]

    @classmethod
    def from_auth(cls, auth) -> UsernamePasswordAuthConfigBackend:
        """

        :param auth:
        :return:
        """
        obj = cls(auth)
        return obj

    @property
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
        else:
            return False


class UsernamePasswordAuth:
    value = 0x02
    transit_to = AUTH

    def __init__(self):
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
        global _username_password_auth

        if not _username_password_auth:
            _username_password_auth = cls()
        _username_password_auth.protocol = protocol

        return _username_password_auth

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

    def auth(self, data: bytes):
        """

        :param data:
        :type data:
        :return:
        :rtype: bool
        """
        ver: int = data[0]
        ulen: int = data[1]
        uname: bytes = data[2 : 2 + ulen]
        plen: int = data[2 + ulen]
        passwd: bytes = data[2 + ulen + 1 : 2 + ulen + 1 + plen]

        if self.backend.authenticate(uname, passwd):
            self.protocol.transport.write(pack("!BB", ver, 0x00))
            self.protocol.state = HOST
        else:
            self.protocol.transport.write(pack("!BB", ver, 0xFF))
            self.protocol.transport.close()
