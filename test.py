#!/usr/bin/env python3
from unittest.mock import Mock
import unittest

from telnetlib import Telnet
import socket

from ctfqa import CTFQA

class TestConstructor(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)

    def test_succeeds(self):
        ctfqa = CTFQA(self.telnet)

if __name__ == '__main__':
    unittest.main()
