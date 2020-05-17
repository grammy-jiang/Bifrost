from unittest.case import TestCase

from bifrost.utils.misc import load_object


class MiscTestCase(TestCase):
    def test_load_object(self):
        obj = load_object("bifrost.utils.misc.load_object")
        self.assertIs(obj, load_object)
