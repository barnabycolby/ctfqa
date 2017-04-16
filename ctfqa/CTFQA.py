#!/usr/bin/env python3
from telnetlib import Telnet

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
        pass


    def setQuestionRegex(self, regex):
        """Set the regex used to identify the questions in the server responses.

        Arguments:
        regex -- The regex used to identify the questions.
        """
        self.setQuestionRegexCalled = True


    def setAnswerCallback(self, callback):
        """Set the callback function that generates the response from the
        question asked by the server.

        Arguments:
        callback -- The callback function.
        """
        self.setAnswerCallbackCalled = True


    def solve(self):
        """
        Solves the CTF challenge by communicating with the telnet server, using
        the answer callback to generate responses.

        Throws:
        NotConfiguredError -- If the CTFQA object has not been fully configured,
                              see the exception message for details.
        """
        if not self.setQuestionRegexCalled:
            raise NotConfiguredError("You need to call setQuestionRegex first.")

        if not self.setAnswerCallbackCalled:
            raise NotConfiguredError("You need to call setAnswerCallback first.")
