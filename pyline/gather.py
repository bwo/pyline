import re
from .utils import *


def gather_int(times, pyl, q):
    answers = []
    for i in range(times):
        answers.append(pyl.ask(question=q))
#        q.prompt = ''
    return answers

def _gather_function(f, pyl, q):
    answers = []
    answers.append(pyl.ask(q))
#    q.prompt = ''
    while not f(answers[-1]):
        answers.append(pyl.ask(q))
    answers.pop()
    return answers

def gather_regexp(pat, pyl, q):
    return _gather_function(pat.search, pyl, q)

def gather_string(s, pyl, q):
    return _gather_function(s.__eq__, pyl, q)

def gather_dict(keys, pyl, q):
    answers = {}
    origprompt = q.prompt
    for key in keys:
        q.prompt = pyl.effectize_string(origprompt, keys={'key':key})
        answers[key] = pyl.ask(q)
    return answers

gather_dispatch = {
    int:gather_int,
    str:gather_string,
    list:gather_dict,
    type(re.compile("s")):gather_regexp
    }
