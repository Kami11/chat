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
        result = AAAManager.hash("test", b"")
        self.assertEqual(b'\x9e\xce\x08n\x9b\xacI\x1f\xac\\\x1d\x10F\xca\x11\xd77\xb9*+.\xbd\x93\xf0\x05\xd7\xb7\x10\x11\x0c\ng\x82\x88\x16n\x7f\xbeyh\x83\xa4\xf2\xe9\xb3\xca\x9fHOR\x1d\x0c\xe4d4\\\xc1\xae\xc9gy\x14\x9c\x14', result)

    def test_two(self):
        result = AAAManager.hash("test", b"\000")
        self.assertEqual(b'\xf3&\xb5\x94\xdbZ\xb7\xa5@\xbd+q\xb6\xb6\xe7\x02\xd9fZ\x0f\x84^ `\x0b\x12\xfa\xcb1\xfe\xa4\x87D\xf6E"\xb5\x85\xb9\x8ex\x8d\xb7\xcdL\xdf\x9eO\xa6-\xc6\x81T\x06\xc3\xb31n>\xb7bm\xfc\x91', result)


    def test_one(self):
        result = AAAManager.hash("abcdef", b"\205\020")
        self.assertEqual(b'/\x18\xc5Z\xa2\xfa\x9aYC,\\\xee\x98\xe6\x88\x93\xe7P\x98\x9dP\xc2.\x1fY\x96\xe0\x91\xb7;\x9f\x01\x948\xf1\xe09\xf3d9m\x92\x88\xba\nL\xbc\x86Ih$\xa2\x1e@\xedU\xb8\x81)\\h\x02\x9c\xe2', result)


    def test_three(self):
        time.sleep(1)
        self.assertEqual(0, 0)

    def test_four(self):
        time.sleep(1)
        self.assertEqual(0, 0)

if __name__ == '__main__':
    unittest.main()
