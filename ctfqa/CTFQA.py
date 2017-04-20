#!/usr/bin/env python3
from telnetlib import Telnet
import inspect
import logging
import re

from ctfqa import NotConfiguredError


"""
This class is designed to make the solving of question and answer style CTF
challenges trivial. Use as follows:

from telnetlib import Telnet
from ctfqa import CTFQA

def answerCallback(...):
    ...

tn = Telnet("127.0.0.1", 1234)
qa = CTFQA(tn)
qa.setQuestionRegex("...")
qa.setAnswerCallback(answerCallback)
qa.solve()
"""
class CTFQA:
    def __init__(self, telnet):
        """Instantiate an instance of the CTFQA class.

        Arguments:
        telnet -- An instance of the telnetlib Telnet class that can be used to
                  communicate with the question and answer server.
        """
        self.setQuestionRegexCalled = False
        self.setAnswerCallbackCalled = False
        self.questionRegex = None
        self.answerCallback = None
        self.telnet = telnet
        self.logger = logging.getLogger(__name__)


    def setQuestionRegex(self, regex):
        """Set the regex used to identify the questions in the server responses.
        The regex must be of the form described by the python re module,
        grouping items that should be selected as arguments for the answer
        callback. For example, if the question is "What is 4 + 6?" and the regex
        is "What is (\d*) \+ (\d*)?", the answer callback will be called with 4
        and 6.

        Arguments:
        regex -- The regex used to identify the questions.

        Throws:
        re.error -- If the regex is invalid.
        """
        self.questionRegex = re.compile(regex)
        self.setQuestionRegexCalled = True
        self.logger.info("Set question regex to \"{}\"".format(regex))


    def setAnswerCallback(self, callback):
        """Set the callback function that generates the response from the
        question asked by the server.

        Arguments:
        callback -- The callback function.

        Throws:
        TypeError -- If the provided callback is not callable.
        """
        if not callable(callback):
            raise TypeError("The argument you provided is not callable.")

        self.answerCallback = callback
        self.setAnswerCallbackCalled = True
        self.logger.info("Set answer callback to {}{}".format(
                callback.__name__,
                inspect.signature(callback))
            )


    def solve(self):
        """
        Solves the CTF challenge by communicating with the telnet server, using
        the answer callback to generate responses. Any unrecognised responses
        are returned.

        Throws:
        NotConfiguredError -- If the CTFQA object has not been fully configured,
                              see the exception message for details.
        ConnectionError -- If the connection is closed by the server unexpectedly.
        """
        if not self.setQuestionRegexCalled:
            exception_message = "You need to call setQuestionRegex first."
            self.logger.error(exception_message)
            raise NotConfiguredError(exception_message)

        if not self.setAnswerCallbackCalled:
            exception_message = "You need to call setAnswerCallback first."
            self.logger.error(exception_message)
            raise NotConfiguredError(exception_message)

        connectionOpen = True
        lastResponse = None
        while connectionOpen:
            try:
                question_bytes = self.telnet.read_until(b"\n", timeout=30)
            except EOFError:
                exception_message = "There is no more output to read."
                self.logger.error(exception_message)
                raise ConnectionError(exception_message)
            question = str(question_bytes, "utf-8")

            matches = self.questionRegex.search(question)
            if matches is None:
                lastResponse = question
                connectionOpen = False
            else:
                answer = self.answerCallback(*matches.groups())
                self.logger.info("Q: {}".format(question.strip()))
                self.logger.info("A: {}".format(answer.strip()))
                try:
                    answer_with_newline = "{}\n".format(answer)
                    self.telnet.write(answer_with_newline.encode())
                except OSError:
                    exception_message = "Tried to write to a closed connection."
                    self.logger.error(exception_message)
                    raise ConnectionError(exception_message)

        self.logger.info("Returning unrecognised response")
        return lastResponse
