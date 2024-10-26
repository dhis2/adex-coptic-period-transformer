import unittest
from main import get_last_day_coptic_month, convert_coptic_quarter, convert_coptic_year, convert_coptic_month


class TestCopticCalendar(unittest.TestCase):

    def test_get_last_day_coptic_month(self):
        self.assertEqual(get_last_day_coptic_month(1736, 1), 30)
        self.assertEqual(get_last_day_coptic_month(1736, 2), 30)
        self.assertEqual(get_last_day_coptic_month(1736, 13), 5)


class TestConvertCopticQuarter(unittest.TestCase):

    def test_convert_coptic_quarter(self):
        self.assertEqual(convert_coptic_quarter('1736Q1'), '2019Q4')
        self.assertEqual(convert_coptic_quarter('1736Q2'), '2020Q1')
        self.assertEqual(convert_coptic_quarter('1740Q4'), '2024Q3')


class TestConvertCopticYear(unittest.TestCase):

    def test_convert_coptic_year(self):
        self.assertEqual(convert_coptic_year('1736'), '2020')
        self.assertEqual(convert_coptic_year('1737'), '2021')
        self.assertEqual(convert_coptic_year('1740'), '2024')

class TestConvertCopticMonth(unittest.TestCase):

    def test_convert_coptic_month(self):
        self.assertEqual(convert_coptic_month('173601'), '201910')
        self.assertEqual(convert_coptic_month('173602'), '201911')
        self.assertEqual(convert_coptic_month('174012'), '202409')
        self.assertEqual(convert_coptic_month('174013'), '202409')

if __name__ == '__main__':
    unittest.main()
