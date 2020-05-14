"""
Test BaseSettings class
"""
from collections.abc import Iterable
from unittest.case import TestCase

from bifrost.exceptions.settings import (
    SettingsFrozenException,
    SettingsLowPriorityException,
)
from bifrost.settings import BaseSettings, Setting


class BaseSettingsTest(TestCase):
    """
    test BaseSettings class
    """

    def setUp(self) -> None:
        self.settings_empty = BaseSettings()
        self.settings = BaseSettings(settings={"a": 1, "b": 2})

    def tearDown(self) -> None:
        del self.settings_empty
        del self.settings

    def test_init(self):
        """
        test the initialize method
        :return:
        """
        self.assertDictEqual(
            self.settings_empty._data, {}  # pylint: disable = protected-access
        )
        self.assertDictEqual(
            self.settings._data,  # pylint: disable = protected-access
            {
                "a": Setting(priority="project", priority_value=20, value=1),
                "b": Setting(priority="project", priority_value=20, value=2),
            },
        )

        self.assertTrue(self.settings.is_frozen())
        self.assertEqual(
            self.settings._priority, "project"  # pylint: disable = protected-access
        )

    def test_is_frozen(self):
        """
        test the method is_frozen
        :return:
        """
        self.assertTrue(self.settings_empty.is_frozen())
        with self.settings_empty.unfreeze() as settings:
            self.assertFalse(settings.is_frozen())

    def test_unfreeze(self):
        """
        test the context manager unfreeze
        :return:
        """
        self.assertTrue(self.settings_empty.is_frozen())
        with self.settings_empty.unfreeze() as settings:
            self.assertFalse(settings.is_frozen())

        self.assertEqual(
            self.settings_empty._priority,  # pylint: disable = protected-access
            "project",
        )
        with self.settings_empty.unfreeze(priority="user") as settings:
            self.assertFalse(settings.is_frozen())
            self.assertEqual(
                settings._priority, "user"  # pylint: disable = protected-access
            )
        self.assertEqual(
            settings._priority, "project"  # pylint: disable = protected-access
        )

    def test_update(self):
        """
        test the method of update
        :return:
        """
        with self.settings_empty.unfreeze() as settings:
            self.assertIsNone(settings.update({"c": 3}))
            self.assertIsNone(settings.update(d=4))
        self.assertDictEqual(
            self.settings_empty._data,  # pylint: disable = protected-access
            {
                "c": Setting(priority="project", priority_value=20, value=3),
                "d": Setting(priority="project", priority_value=20, value=4),
            },
        )

        with self.settings_empty.unfreeze() as settings:
            self.assertIsNone(settings.update({"c": 5}))
            self.assertIsNone(settings.update(d=6))
        self.assertDictEqual(
            self.settings_empty._data,  # pylint: disable = protected-access
            {
                "c": Setting(priority="project", priority_value=20, value=5),
                "d": Setting(priority="project", priority_value=20, value=6),
            },
        )

    def test_getitem(self):
        """
        test the method of getitem
        :return:
        """
        self.assertEqual(self.settings["a"], 1)

    def test_setitem(self):
        """
        test the method of setitem
        :return:
        """
        with self.settings.unfreeze() as settings:
            settings["c"] = 3
        self.assertEqual(settings["c"], 3)

        with self.assertRaises(SettingsFrozenException):
            self.settings["c"] = 3

        with self.assertRaises(SettingsLowPriorityException):
            with self.settings.unfreeze("default") as settings:
                settings["a"] = 3

    def test_delitem(self):
        """
        test the method of del
        :return:
        """
        with self.settings.unfreeze() as settings:
            del settings["a"]
        self.assertNotIn("a", self.settings)

        with self.assertRaises(SettingsFrozenException):
            del self.settings["a"]

    def test_iter(self):
        """
        test the method of iter
        :return:
        """
        self.assertIsInstance(self.settings, Iterable)

    def test_len(self):
        """
        test the method of len
        :return:
        """
        self.assertEqual(len(self.settings), 2)
        self.assertEqual(len(self.settings_empty), 0)

    def test_contains(self):
        """
        test the method of contains
        :return:
        """
        self.assertTrue("a" in self.settings)
        self.assertFalse("c" in self.settings)
