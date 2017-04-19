#unit_tests.py

import unittest
#from kisschat.server import main

class TestsForAddFunction(unittest.TestCase):

    def test_zeros(self):
        
        self.assertEqual(0, 0)

#    def test_one(self):
#        result = add_two_numbers(1, 2)
#        self.assertEqual(3, result)
#
#    def test_two(self):
#        result = add_two_numbers(-1, 1)
#        self.assertEqual(0, result)

if __name__ == '__main__':
    unittest.main()
