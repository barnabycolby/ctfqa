# CTFQA
This python 3.5+ library makes solving CTF question and answer style scripting challenges easy. Simply set a question regex used to identify and parse the questions and an answer callback that generates the corresponding response.

## Example usage
The example below could be used with a server that asks questions such as `What is 5 + 4?`.
```python
#!/usr/bin/env python3.5
from ctfqa import CTFQA
from telnetlib import Telnet

def add(a, b):
    return str(int(a) + int(b))

tn = Telnet("localhost", "1234")
ctfqa = CTFQA(tn)
ctfqa.setQuestionRegex("What is (\d*) \+ (\d*)\?")
ctfqa.setAnswerCallback(add)
last_response = ctfqa.solve()
```
The `last_response` variable will contain any response not recognised as a question, which, if solved correctly should contain the flag.

## Debugging
The library logs it's conversation with the server. To see this output, simply add the following lines to your code:
```python
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
```
