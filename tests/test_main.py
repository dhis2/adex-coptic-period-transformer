import unittest
from main import convert_ethiopian_day, convert_ethiopian_week, convert_ethiopian_year, convert_ethiopian_month, \
    handle_period, convert_ethiopian_period, convert_ethiopian_quarter


class TestConvertEthiopianDay(unittest.TestCase):

    def test_convert_ethiopian_day(self):
        self.assertEqual(convert_ethiopian_day('20170221'), '20241031')
        self.assertEqual(convert_ethiopian_day('20170222'), '20241101')
        self.assertEqual(convert_ethiopian_day('20161301'), '20240906')


class TestConvertEthiopianWeek(unittest.TestCase):

    def test_convert_ethiopian_week(self):
        self.assertEqual(convert_ethiopian_week('2015W53'), '2023W36')
        self.assertEqual(convert_ethiopian_week('2016W1'), '2023W37')
        self.assertEqual(convert_ethiopian_week('2016W2'), '2023W38')
        self.assertEqual(convert_ethiopian_week('2016W3'), '2023W39')


class TestConvertEthiopianYear(unittest.TestCase):

    def test_convert_ethiopian_year(self):
        self.assertEqual(convert_ethiopian_year('2013'), '2021')
        self.assertEqual(convert_ethiopian_year('2014'), '2022')
        self.assertEqual(convert_ethiopian_year('2015'), '2023')
        self.assertEqual(convert_ethiopian_year('2016'), '2024')
        self.assertEqual(convert_ethiopian_year('2017'), '2025')
        self.assertEqual(convert_ethiopian_year('2018'), '2026')
        self.assertEqual(convert_ethiopian_year('2019'), '2027')
        self.assertEqual(convert_ethiopian_year('2020'), '2028')


class TestConvertEthiopianMonth(unittest.TestCase):
    def test_convert_ethiopian_month(self):
        self.assertEqual(convert_ethiopian_month('201701'), '202410')
        self.assertEqual(convert_ethiopian_month('201712'), '202509')
        self.assertEqual(convert_ethiopian_month('201713'), '202509')


class TestConvertEthiopianQuarter(unittest.TestCase):

    def test_convert_ethiopian_quarter(self):
        self.assertEqual(convert_ethiopian_quarter('2017Q1'), '2024Q2')
        self.assertEqual(convert_ethiopian_quarter('2017Q2'), '2024Q3')
        self.assertEqual(convert_ethiopian_quarter('2017Q3'), '2024Q4')
        self.assertEqual(convert_ethiopian_quarter('2017Q4'), '2025Q1')


class TestConvertEthiopianPeriod(unittest.TestCase):

    def test_convert_ethiopian_period(self):
        self.assertEqual(convert_ethiopian_period('20170221'), '20241031')
        self.assertEqual(convert_ethiopian_period('2017'), '2025')
        self.assertEqual(convert_ethiopian_period('2015W53'), '2023W36')
        self.assertEqual(convert_ethiopian_period('2016W1'), '2023W37')
        self.assertEqual(convert_ethiopian_period('201612'), '202409')
        self.assertEqual(convert_ethiopian_period('2017Q1'), '2024Q4')


class TestConvertDataValueSet(unittest.TestCase):

    def test_convert_data_value_set(self):
        data_value_set_ethiopian = {
            'dataValues': [
                {'period': '20170221'},
                {'period': '2017'},
                {'period': '2017Q1'}
            ]
        }
        data_value_set_gregorian = {
            'dataValues': [
                {'period': '20241031'},
                {'period': '2025'},
                {'period': '2024Q4'}
            ]
        }

        self.assertEqual(handle_period(data_value_set_ethiopian), data_value_set_gregorian)


if __name__ == '__main__':
    unittest.main()
