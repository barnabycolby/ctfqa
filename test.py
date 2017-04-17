#!/usr/bin/env python3
from unittest.mock import call, Mock
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
        expected_flag = "flag{b34n5_4nd_s4us463s}"
        self.telnet.read_until.side_effect = [
                "What is 6 + 4?",
                "What is 145 + 208?",
                "What is 43717893 + 327890432?",
                expected_flag,
                EOFError()
            ]

        # The callback function that is used to generate the answer
        def add(a, b):
            return str(int(a) + int(b))

        self.ctfqa.setQuestionRegex("What is (\d*) \+ (\d*)\?")
        self.ctfqa.setAnswerCallback(add)
        actual_flag = self.ctfqa.solve()

        self.telnet.read_until.assert_has_calls([
                call("\n"),
                call("\n"),
                call("\n")
            ])
        self.telnet.write.assert_has_calls([
                call("10\n"),
                call("353\n"),
                call("371608325\n")
            ])
        self.assertEqual(expected_flag, actual_flag)


    def test_solve_connection_closed(self):
        self.telnet.read_until.side_effect = EOFError()

        # The callback function that is used to generate the answer
        def multiply(a, b):
            return str(int(a) * int(b))

        self.ctfqa.setQuestionRegex("(\d*) \* (\d*)")
        self.ctfqa.setAnswerCallback(multiply)
        with self.assertRaises(EOFError):
            self.ctfqa.solve()


if __name__ == '__main__':
    unittest.main()
