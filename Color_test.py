import unittest
from Color import Color

class TestColor(unittest.TestCase):

    # =============================================================
    # test correct initialization

    def test_should_create_color_from_rgb_single_values(self):
        self.assertEqual(Color(r=1,g=2,b=3).to_tuple(),(1,2,3))
        
    def test_should_create_color_from_rgb_tuple_values(self):
        self.assertEqual(Color(rgb=(41,42,43)).to_tuple(),(41,42,43))
        
    def test_should_create_color_from_hex_values(self):
        self.assertEqual(Color(_hex='fFAa00').to_tuple(),(255,170,0))
                
    def test_should_create_color_from_predefined_values(self):
        self.assertEqual(Color(rgb=Color.RED).to_tuple(),(255,0,0))

    # =============================================================
    # test wrong initialization

    def test_should_raise_error_on_no_arguments(self):
        with self.assertRaises(ValueError):
            test_var = Color()

    def test_should_raise_error_on_wrong_rgb_single_arguments(self):
        with self.assertRaises(ValueError):
            test_var = Color(r=-1, g=13, b=14)
        with self.assertRaises(ValueError):
            test_var = Color(r=256, g=13, b=14)

    def test_should_raise_error_on_wrong_rgb_tuple_arguments(self):
        with self.assertRaises(ValueError):
            test_var = Color(rgb=(-1,13,14))
        with self.assertRaises(ValueError):
            test_var = Color(rgb=(256,13,14))
        with self.assertRaises(ValueError):
            test_var = Color(rgb=(13,14))
        with self.assertRaises(ValueError):
            test_var = Color(rgb=(12,13,14,15))

    def test_should_raise_error_on_wrong_hex_arguments(self):
        with self.assertRaises(ValueError):
            test_var = Color(_hex='bzdura')
        with self.assertRaises(ValueError):
            test_var = Color(_hex='abababab')
        with self.assertRaises(ValueError):
            test_var = Color(_hex='123456789')
        with self.assertRaises(ValueError):
            test_var = Color(_hex='abc')
        with self.assertRaises(ValueError):
            test_var = Color(_hex='xyzxyz')
        with self.assertRaises(ValueError):
            test_var = Color(_hex='*$^%@#(')

    # =============================================================
    # test opacity

    def test_should_apply_opacity_case1(self):
        bg_color = Color(rgb=Color.BLACK)
        color1 = Color(rgb=(100,50,200))
        opacity = 0.5
        self.assertEqual(color1.apply_opacity(bg_color, opacity).to_tuple(),
                         (50,25,100))
        opacity = 0.25
        self.assertEqual(color1.apply_opacity(bg_color, opacity).to_tuple(),
                         (25,12,50))

    def test_should_apply_opacity_case2(self):
        bg_color = Color(rgb=(100,100,100))
        color1 = Color(rgb=(100,60,30))
        opacity = 0.5
        self.assertEqual(color1.apply_opacity(bg_color, opacity).to_tuple(),
                         (100,80,65))
        print(bg_color.to_tuple())
        print(color1.to_tuple())
        opacity = 0.75
        self.assertEqual(color1.apply_opacity(bg_color, opacity).to_tuple(),
                         (100,70,48))

    # =============================================================
    # test adding and subtracting

    def test_should_add_colors_case1(self):
        color1 = Color(rgb=(1,2,3))
        color2 = Color(rgb=(11,12,13))
        self.assertEqual((color1 + color2).to_tuple(), (12,14,16))

    def test_should_add_colors_case2(self):
        color1 = Color(rgb=(1,2,3))
        color2 = Color(rgb=(255,255,255))
        self.assertEqual((color1 + color2).to_tuple(), (256,257,258))

    def test_should_subtract_colors_case1(self):
        color1 = Color(rgb=(11,12,13))
        color2 = Color(rgb=(1,2,3))
        self.assertEqual((color1 - color2).to_tuple(), (10,10,10))

    def test_should_subtract_colors_case2(self):
        color1 = Color(rgb=(1,2,3))
        color2 = Color(rgb=(11,12,13))
        self.assertEqual((color1 - color2).to_tuple(), (-10,-10,-10))

    # =============================================================
    # test summing

    def test_should_sum_color(self):
        self.assertEqual(Color(rgb=(13,18,22)).sum(), 53)

    # =============================================================
    # test corrections

    def test_should_correct_minimum_average(self):
        # given
        color_low_average = Color(rgb=(20,20,20))
        # when
        color_low_average.correct_minimum_average(60)
        # then
        self.assertGreaterEqual(color_low_average.sum(), 60)

# #############################################################
# SUITES

def suite_constructor():
    suite = unittest.TestSuite()
    suite.addTest(TestColor('test_should_create_color_from_rgb_single_values'))
    suite.addTest(TestColor('test_should_create_color_from_rgb_tuple_values'))
    suite.addTest(TestColor('test_should_create_color_from_hex_values'))
    suite.addTest(TestColor('test_should_create_color_from_predefined_values'))
    return suite

def suite_constructor_wrong_calls():
    suite = unittest.TestSuite()
    suite.addTest(TestColor('test_should_raise_error_on_no_arguments'))
    suite.addTest(TestColor('test_should_raise_error_on_wrong_rgb_single_arguments'))
    suite.addTest(TestColor('test_should_raise_error_on_wrong_rgb_tuple_arguments'))
    suite.addTest(TestColor('test_should_raise_error_on_wrong_hex_arguments'))
    return suite

def suite_opacity():
    suite = unittest.TestSuite()
    suite.addTest(TestColor('test_should_apply_opacity_case1'))
    suite.addTest(TestColor('test_should_apply_opacity_case2'))
    return suite

def suite_add_subtract():
    suite = unittest.TestSuite()
    suite.addTest(TestColor('test_should_add_colors_case1'))
    suite.addTest(TestColor('test_should_add_colors_case2'))
    suite.addTest(TestColor('test_should_subtract_colors_case1'))
    suite.addTest(TestColor('test_should_subtract_colors_case2'))
    return suite

def suite_summing():
    suite = unittest.TestSuite()
    suite.addTest(TestColor('test_should_sum_color'))
    return suite

def suite_corrections():
    suite = unittest.TestSuite()
    suite.addTest(TestColor('test_should_correct_minimum_average'))
    return suite

# #############################################################
# main

def suite_intro(name):
    print()
    print()
    print('*'*79)
    print(name)
    print('*'*79)
    print()
    print()

def run_suite(runner, suite_generator, name):
    suite_intro(name)
    suite = suite_generator()
    runner.run(suite)
    return len(suite._tests)
    
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    total_tests = 0
    expected_tests = 0
    for x in dir(TestColor):
        if x.startswith('test_'):
            expected_tests += 1

    total_tests += run_suite(runner, suite_constructor, 'CONSTRUCTOR - GOOD CALLS')
    total_tests += run_suite(runner, suite_constructor_wrong_calls, 'CONSTRUCTOR - WRONG CALLS')
    total_tests += run_suite(runner, suite_opacity, 'OPACITY')
    total_tests += run_suite(runner, suite_add_subtract, 'ADDING AND SUBTRACTING')
    total_tests += run_suite(runner, suite_summing, 'SUMMING')
    total_tests += run_suite(runner, suite_corrections, 'CORRECTIONS')

    suite_intro('SUITE COMPLETENESS')
    print('Tests ran: ' + str(total_tests))
    print('Tests omitted: ' + str(expected_tests - total_tests))

    suite_intro('END')
    
