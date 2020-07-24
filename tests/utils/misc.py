import asyncio
from unittest.case import TestCase

from bifrost.utils.misc import load_object, to_async, to_bytes, to_str, to_sync


class MiscTestCase(TestCase):
    def test_load_object(self):
        obj = load_object("bifrost.utils.misc.load_object")
        self.assertIs(obj, load_object)

    def test_to_bytes(self):
        self.assertEqual(to_bytes("a"), b"a")
        self.assertEqual(to_bytes(b"a"), b"a")
        with self.assertRaises(TypeError):
            to_bytes(0)

    def test_to_str(self):
        self.assertEqual(to_str(b"a"), "a")
        self.assertEqual(to_str("a"), "a")
        with self.assertRaises(TypeError):
            to_str(0)

    def test_to_sync(self):
        @to_sync
        def sync_func(a, b, c=None):
            return a, b, c

        self.assertSequenceEqual(sync_func("a", "b", "c"), ("a", "b", "c"))

        @to_sync
        async def async_func(a, b, c=None):
            return a, b, c

        self.assertSequenceEqual(async_func("a", "b", "c"), ("a", "b", "c"))

    def test_to_async(self):
        loop = asyncio.get_event_loop()

        @to_async
        def sync_func(a, b, c=None):
            return a, b, c

        self.assertSequenceEqual(
            loop.run_until_complete(sync_func("a", "b", "c")), ("a", "b", "c")
        )

        @to_async
        async def async_func(a, b, c=None):
            return a, b, c

        self.assertSequenceEqual(
            loop.run_until_complete(async_func("a", "b", "c")), ("a", "b", "c")
        )
