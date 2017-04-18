#!/usr/bin/env python3
from telnetlib import Telnet
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
            raise NotConfiguredError("You need to call setQuestionRegex first.")

        if not self.setAnswerCallbackCalled:
            raise NotConfiguredError("You need to call setAnswerCallback first.")

        connectionOpen = True
        lastResponse = None
        while connectionOpen:
            try:
                question_bytes = self.telnet.read_until(b"\n", timeout=30)
            except EOFError:
                raise ConnectionError("There is no more output to read.")
            question = str(question_bytes, "utf-8")

            matches = self.questionRegex.search(question)
            if matches is None:
                lastResponse = question
                connectionOpen = False
            else:
                answer = self.answerCallback(*matches.groups())
                try:
                    answer_with_newline = "{}\n".format(answer)
                    self.telnet.write(answer_with_newline.encode())
                except OSError:
                    raise ConnectionError("Tried to write to a closed connection.")

        return lastResponse
