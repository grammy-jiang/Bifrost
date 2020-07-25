from unittest import TestCase

from bifrost.protocols.socks5 import (
    Socks5Protocol,
    Socks5StateAuth,
    Socks5StateData,
    Socks5StateHost,
    Socks5StateInit,
)


class Socks5Test(TestCase):
    def setUp(self):
        channel = object()
        self.protocol = Socks5Protocol(channel)

    def tearDown(self):
        del self.protocol

    def test_state_machine_init(self):
        self.assertIsInstance(self.protocol.state, Socks5StateInit)

    def test_state_machine_switch(self):
        self.protocol.state.switch()
        self.assertIsInstance(self.protocol.state, Socks5StateAuth)

        self.protocol.state.switch()
        self.assertIsInstance(self.protocol.state, Socks5StateHost)

        self.protocol.state.switch()
        self.assertIsInstance(self.protocol.state, Socks5StateData)
