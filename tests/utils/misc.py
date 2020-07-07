from unittest.case import TestCase

from bifrost.utils.misc import load_object, to_bytes, to_str


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
