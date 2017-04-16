#!/usr/bin/env python3
from telnetlib import Telnet

from ctfqa import NotConfiguredError

class CTFQA:
    def __init__(self, telnet):
        self.setQuestionRegexCalled = False
        self.setAnswerCallbackCalled = False
        pass


    def setQuestionRegex(self, regex):
        self.setQuestionRegexCalled = True


    def setAnswerCallback(self, callback):
        self.setAnswerCallbackCalled = True


    def solve(self):
        if not self.setQuestionRegexCalled:
            raise NotConfiguredError("You need to call setQuestionRegex first.")

        if not self.setAnswerCallbackCalled:
            raise NotConfiguredError("You need to call setAnswerCallback first.")
