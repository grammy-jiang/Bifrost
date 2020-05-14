"""
Test Settings class
"""
from unittest.case import TestCase

from bifrost.settings import Setting, Settings, defaults


class SettingsTest(TestCase):
    """
    test Settings class
    """

    def setUp(self) -> None:
        self.settings = Settings()

    def tearDown(self) -> None:
        del self.settings

    def test_update_from_module(self):
        """
        test the method of update_from_module
        :return:
        """
        with self.settings.unfreeze(priority="env") as settings:
            settings.update_from_module(defaults)
        self.assertIn("LOOP", self.settings)
        self.assertEqual(
            self.settings._data["LOOP"],  # pylint: disable = protected-access
            Setting(priority="env", priority_value=30, value="uvloop"),
        )
