#!/usr/bin/env python3
from unittest.mock import Mock
import unittest

from telnetlib import Telnet
import socket

from ctfqa import CTFQA, NotConfiguredError


class TestConstructor(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)


    def test_succeeds(self):
        ctfqa = CTFQA(self.telnet)


class TestSolve(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)
        self.ctfqa = CTFQA(self.telnet)


    def test_question_regex_not_set(self):
        self.ctfqa.setAnswerCallback(lambda *args: None)
        exception_message = "You need to call setQuestionRegex first\."
        with self.assertRaisesRegex(NotConfiguredError, exception_message):
            self.ctfqa.solve()


    def test_answer_callback_not_set(self):
        self.ctfqa.setQuestionRegex("")
        exception_message = "You need to call setAnswerCallback first\."
        with self.assertRaisesRegex(NotConfiguredError, exception_message):
            self.ctfqa.solve()


    def test_solve_succeeds(self):
        self.ctfqa.setQuestionRegex("")
        self.ctfqa.setAnswerCallback(lambda *args: None)
        self.ctfqa.solve()


if __name__ == '__main__':
    unittest.main()
