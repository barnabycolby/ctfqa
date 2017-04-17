#!/usr/bin/env python3
from unittest.mock import call, Mock
import unittest

from telnetlib import Telnet
import re
import socket

from ctfqa import CTFQA, NotConfiguredError


class TestConstructor(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)


    def test_succeeds(self):
        ctfqa = CTFQA(self.telnet)


class TestSetQuestionRegex(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)
        self.ctfqa = CTFQA(self.telnet)


    def test_invalid_regex(self):
        with self.assertRaises(re.error):
            self.ctfqa.setQuestionRegex("[")


    def test_succeeds(self):
        self.ctfqa.setQuestionRegex("(\d*)")


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
                call("\n", timeout=30),
                call("\n", timeout=30),
                call("\n", timeout=30)
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
        exception_message = "There is no more output to read."
        with self.assertRaisesRegex(ConnectionError, exception_message):
            self.ctfqa.solve()


    def test_solve_connection_closed_halfway(self):
        self.telnet.read_until.side_effect = [
                "3 * 8",
                EOFError()
            ]

        # The callback function that is used to generate the answer
        def multiply(a, b):
            return str(int(a) * int(b))

        self.ctfqa.setQuestionRegex("(\d*) \* (\d*)")
        self.ctfqa.setAnswerCallback(multiply)
        exception_message = "There is no more output to read."
        with self.assertRaisesRegex(ConnectionError, exception_message):
            self.ctfqa.solve()

        self.telnet.read_until.assert_has_calls([
                call("\n", timeout=30),
                call("\n", timeout=30)
            ])
        self.telnet.write.assert_called_once_with("24\n")


    def test_solve_incorrect_answer_response(self):
        expected_last_response = "WRONG"
        self.telnet.read_until.side_effect = [
                "Please add 4 and 9:",
                "Please add 105 and 87:",
                expected_last_response,
                EOFError()
            ]

        # The callback function that is used to generate the answer
        def add(a, b):
            return str(int(a) + int(b))

        self.ctfqa.setQuestionRegex("Please add (\d*) and (\d*):")
        self.ctfqa.setAnswerCallback(add)
        actual_last_response = self.ctfqa.solve()

        self.telnet.read_until.assert_has_calls([
                call("\n", timeout=30),
                call("\n", timeout=30),
                call("\n", timeout=30)
            ])
        self.telnet.write.assert_has_calls([
                call("13\n"),
                call("192\n")
            ])
        self.assertEqual(expected_last_response, actual_last_response)


    def test_solve_os_error(self):
        self.telnet.read_until.side_effect = [
                "'Concatenate' 'this string together'"
            ]
        self.telnet.write.side_effect = [
                OSError()
            ]

        # The callback function that is used to generate the answer
        def concatenate(a, b):
            return "{} {}".format(a, b)

        self.ctfqa.setQuestionRegex("'([^']*)' '([^']*)'")
        self.ctfqa.setAnswerCallback(concatenate)

        exception_message = "Tried to write to a closed connection."
        with self.assertRaisesRegex(ConnectionError, exception_message):
            self.ctfqa.solve()


if __name__ == '__main__':
    unittest.main()
