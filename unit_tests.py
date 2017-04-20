#unit_tests.py

import unittest
import time
import datetime
from kisschat.chat.chatmanager import ChatManager
from kisschat.chat.aaamanager import AAAManager

class TestsForAddFunction(unittest.TestCase):


    def test_zeros(self):
        result = ChatManager.time()
       	time = datetime.datetime.now().time()
       	self.assertEqual("[{:02}:{:02}]".format(time.hour, time.minute), result)
        
    def test_one(self):
        result = AAAManager.hash("test", bytes(0x00))
        self.assertEqual(b'test', result)

    def test_two(self):
        result = AAAManager.hash("test", bytes(0x01))
        self.assertEqual(b'\xf5\x9c\xdaFi\xaf\x0e\xe79\x96\xbes\x00\xd4\xb0\xff\x86\x0cK\xaa\xc6K\x9b{\x03\xe1}\x03\xfe\xf8z\x17U\xea\x0b\x183C."t5X\x96jc\xffnpp\xae\xa2\x84\'H\xe3S0\xbc2\x94\xf0\xe4\xe7', result)


    def test_one(self):
        result = AAAManager.hash("abcdef", bytes(0x02))
        self.assertEqual(b".\xe0\xeeg\x03\xca\x11T\xea\x820\xe2\xeeP\x85\xed\xce\x07?&\\\x06\xffS\x87\x0f'n\xb1.\xfe\x88\x81\xd2\x81\xe8\x87\x87*\xba\x93az\x88\x8a\xcfO<\xd3diQ\x91\x85\xe1*L\x84\x0c\xdd\xb0\xcb\xc9\xe5", result)


    def test_three(self):
        time.sleep(1)
        self.assertEqual(0, 0)

    def test_four(self):
        time.sleep(1)
        self.assertEqual(0, 0)

if __name__ == '__main__':
    unittest.main()
