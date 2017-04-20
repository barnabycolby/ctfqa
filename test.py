#!/usr/bin/env python3
from testfixtures import LogCapture
from unittest.mock import call, Mock
import unittest

from telnetlib import Telnet
import re
import socket

from ctfqa import CTFQA, NotConfiguredError

MODULE_NAME = "ctfqa.CTFQA"


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
        with LogCapture() as log_capture:
            self.ctfqa.setQuestionRegex("(\d*)")
            log_capture.check(
                (MODULE_NAME, "INFO", "Set question regex to \"(\d*)\"")
            )


class TestSetAnswerCallback(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)
        self.ctfqa = CTFQA(self.telnet)


    def test_invalid_callback(self):
        exception_message = "The argument you provided is not callable."
        with self.assertRaisesRegex(TypeError, exception_message):
            self.ctfqa.setAnswerCallback("Hmmmm")


    def test_succeeds(self):
        def testFunction(firstArg):
            return "1"

        with LogCapture() as log_capture:
            self.ctfqa.setAnswerCallback(testFunction)
            log_capture.check(
                (MODULE_NAME, "INFO", "Set answer callback to testFunction(firstArg)")
            )


class TestSolve(unittest.TestCase):
    def setUp(self):
        self.telnet = Mock(spec=Telnet)
        self.ctfqa = CTFQA(self.telnet)


    def test_question_regex_not_set(self):
        self.ctfqa.setAnswerCallback(lambda *args: None)
        exception_message = "You need to call setQuestionRegex first."
        with LogCapture() as log_capture:
            with self.assertRaisesRegex(NotConfiguredError, exception_message):
                self.ctfqa.solve()
            log_capture.check(
                (MODULE_NAME, "ERROR", exception_message)
            )


    def test_answer_callback_not_set(self):
        self.ctfqa.setQuestionRegex("")
        exception_message = "You need to call setAnswerCallback first."
        with LogCapture() as log_capture:
            with self.assertRaisesRegex(NotConfiguredError, exception_message):
                self.ctfqa.solve()
            log_capture.check(
                (MODULE_NAME, "ERROR", exception_message)
            )


    def test_solve_succeeds(self):
        expected_flag = "flag{b34n5_4nd_s4us463s}"
        self.telnet.read_until.side_effect = [
                b"What is 6 + 4?",
                b"What is 145 + 208?",
                b"What is 43717893 + 327890432?",
                expected_flag.encode(),
                EOFError()
            ]

        # The callback function that is used to generate the answer
        def add(a, b):
            return str(int(a) + int(b))

        self.ctfqa.setQuestionRegex("What is (\d*) \+ (\d*)\?")
        self.ctfqa.setAnswerCallback(add)

        with LogCapture() as log_capture:
            actual_flag = self.ctfqa.solve()
            log_capture.check(
                (MODULE_NAME, "INFO", "Q: What is 6 + 4?"),
                (MODULE_NAME, "INFO", "A: 10"),
                (MODULE_NAME, "INFO", "Q: What is 145 + 208?"),
                (MODULE_NAME, "INFO", "A: 353"),
                (MODULE_NAME, "INFO", "Q: What is 43717893 + 327890432?"),
                (MODULE_NAME, "INFO", "A: 371608325"),
                (MODULE_NAME, "INFO", "Returning unrecognised response")
            )

        self.telnet.read_until.assert_has_calls([
                call(b"\n", timeout=30),
                call(b"\n", timeout=30),
                call(b"\n", timeout=30)
            ])
        self.telnet.write.assert_has_calls([
                call(b"10\n"),
                call(b"353\n"),
                call(b"371608325\n")
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
        with LogCapture() as log_capture:
            with self.assertRaisesRegex(ConnectionError, exception_message):
                self.ctfqa.solve()
            log_capture.check(
                (MODULE_NAME, "ERROR", exception_message)
            )


    def test_solve_connection_closed_halfway(self):
        self.telnet.read_until.side_effect = [
                b"3 * 8",
                EOFError()
            ]

        # The callback function that is used to generate the answer
        def multiply(a, b):
            return str(int(a) * int(b))

        self.ctfqa.setQuestionRegex("(\d*) \* (\d*)")
        self.ctfqa.setAnswerCallback(multiply)
        exception_message = "There is no more output to read."
        with LogCapture() as log_capture:
            with self.assertRaisesRegex(ConnectionError, exception_message):
                self.ctfqa.solve()
            log_capture.check(
                (MODULE_NAME, "INFO", "Q: 3 * 8"),
                (MODULE_NAME, "INFO", "A: 24"),
                (MODULE_NAME, "ERROR", exception_message)
            )

        self.telnet.read_until.assert_has_calls([
                call(b"\n", timeout=30),
                call(b"\n", timeout=30)
            ])
        self.telnet.write.assert_called_once_with(b"24\n")


    def test_solve_incorrect_answer_response(self):
        expected_last_response = "WRONG"
        self.telnet.read_until.side_effect = [
                b"Please add 4 and 9:",
                b"Please add 105 and 87:",
                expected_last_response.encode(),
                EOFError()
            ]

        # The callback function that is used to generate the answer
        def add(a, b):
            return str(int(a) + int(b))

        self.ctfqa.setQuestionRegex("Please add (\d*) and (\d*):")
        self.ctfqa.setAnswerCallback(add)
        actual_last_response = self.ctfqa.solve()

        self.telnet.read_until.assert_has_calls([
                call(b"\n", timeout=30),
                call(b"\n", timeout=30),
                call(b"\n", timeout=30)
            ])
        self.telnet.write.assert_has_calls([
                call(b"13\n"),
                call(b"192\n")
            ])
        self.assertEqual(expected_last_response, actual_last_response)


    def test_solve_os_error(self):
        self.telnet.read_until.side_effect = [
                b"'Concatenate' 'this string together'"
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
        with LogCapture() as log_capture:
            with self.assertRaisesRegex(ConnectionError, exception_message):
                self.ctfqa.solve()
            log_capture.check(
                (MODULE_NAME, "INFO", "Q: 'Concatenate' 'this string together'"),
                (MODULE_NAME, "INFO", "A: Concatenate this string together"),
                (MODULE_NAME, "ERROR", exception_message)
            )


if __name__ == '__main__':
    unittest.main()
