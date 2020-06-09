from unittest import TestCase

from bifrost.utils.unit_converter import convert_unit


class UnitConverterTest(TestCase):
    def test_convert_unit(self):
        self.assertTupleEqual(convert_unit(1), (1, "B"))
        self.assertTupleEqual(convert_unit(1024), (1, "KiB"))
        self.assertTupleEqual(convert_unit(1024 * 512), (512, "KiB"))
        self.assertTupleEqual(convert_unit(1024 * 1024), (1, "MiB"))
        self.assertTupleEqual(convert_unit(1024 * 1024 * 1024), (1, "GiB"))

        self.assertTupleEqual(convert_unit(1, rate=True), (1, "bps"))
        self.assertTupleEqual(convert_unit(1024, rate=True), (1, "Kibit/s"))
        self.assertTupleEqual(convert_unit(1024 * 512, rate=True), (512, "Kibit/s"))
        self.assertTupleEqual(convert_unit(1024 * 1024, rate=True), (1, "Mibit/s"))
        self.assertTupleEqual(
            convert_unit(1024 * 1024 * 1024, rate=True), (1, "Gibit/s")
        )
