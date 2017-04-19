#unit_tests.py

import unittest
import time
import datetime
from kisschat.chat.chatmanager import ChatManager
from kisschat.chat import aaamanager

class TestsForAddFunction(unittest.TestCase):


    def test_zeros(self):
        result = ChatManager.time()
       	time = datetime.datetime.now().time()
       	self.assertEqual("[{:02}:{:02}]".format(time.hour, time.minute), result)
    
    def test_one(self):
        time.sleep(3)
        self.assertEqual(0, 0)

#    def test_one(self):
#        time.sleep(3)
#        result = add_two_numbers(1, 2)
#        self.assertEqual(3, result)
#
#    def test_two(self):
#        result = add_two_numbers(-1, 1)
#        self.assertEqual(0, result)

if __name__ == '__main__':
    unittest.main()
