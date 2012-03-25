import re
import pytest
import pyline.pyline
import pyline.question
import pyline.answers
from conftest import *

def test_agree():
    inp = sio("y\nyes\nYES\nHell no!\nNo\n")
    p = pyline.pyline.PyLine(inp=inp)
    outs = []
    for i in range(4):
        outs.append(p.agree("Yes or no?  "))
    assert outs == [True, True, True, False]
    reset(inp)
    set_inp(inp, "yYyn")
    outs = []
    for i in range(4):
        outs.append(p.agree("Yes or no? ", True))
    assert outs == [True, True, True, False]
    with pytest.raises(EOFError):
        p.agree("")
    set_inp(inp, '\n\n')
    r = p.agree("yes or no? ", default="y")
    r2 = p.agree("yes or no? ", default="n")
    assert r == True and r2 == False

def test_ask():
    inp = sio()
    name = 'Martin Chuzzlewit'
    print >> inp, name
    inp.seek(0)
    p = pyline.pyline.PyLine(inp=inp)
    result = p.ask(prompt='What is your name?  ')
    assert result == name
    with pytest.raises(EOFError):
        p.ask(prompt='more input? ')

def test_autocomplete():
    inp = sio()
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    q = pyline.question.Question("What is your favorite? ", ["perl","python","ruby"])
    set_inp(inp, "p\npy\n")
    res = p.ask(q)
    assert no_clear(out.getvalue()) == 'What is your favorite? Ambiguous match: could be any of python or perl\n? '
    assert res == 'python'

def test_case():
    inp = sio()
    p = pyline.pyline.PyLine(inp=inp)
    q = pyline.question.Question("What are your initials? ", pyline.answers.Answer(), case=pyline.question.upcase)
    set_inp(inp,"baw\n")
    res = p.ask(q)
    assert res == 'BAW'
    set_inp(inp,"fOwL")
    q.case = pyline.question.downcase
    res = p.ask(q)
    assert res == 'fowl'

def test_character_echo():
    inp = sio("password\n")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    q = pyline.question.Question("Enter your password: ", pyline.answers.Answer(),
                                 echo='*')
    p.ask(q)
    assert no_clear(out.getvalue()) == 'Enter your password: ********\n'
    q = pyline.question.Question("Select an option (1, 2, 3): ", pyline.answers.IntAnswer(),
                                 echo='*', character=True)
    set_inp(inp, '2')
    reset(out)
    res = p.ask(q)
    assert res == 2
    assert no_clear(out.getvalue()) == 'Select an option (1, 2, 3): *'

def test_backspace_does_not_enter_prompt():
    inp = sio("a\b\b\b\n")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    q = pyline.question.Question("Please enter your password: ", pyline.answers.Answer(), echo="*")
    ans = p.ask(q)
    assert ans == ''
    assert no_clear(out.getvalue()) == 'Please enter your password: *\b\x1b[P\n'

def test_character_reading():
    inp = sio("12345")
    p = pyline.pyline.PyLine(inp=inp)
    q = pyline.question.Question("Digit: ", int, character=pyline.question.getc)
    ans = p.ask(q)
    assert ans == 1

def test_confirm():
    inp = sio("junk.txt\nno\nsave.txt\ny\n")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    q = pyline.question.Question("Enter a filename:  ",
                                 confirm=lambda s: "Are you sure you want to overwrite {0}? ".format(s),
                                 ask_on_error=pyline.question.repeat_question)
    answer = p.ask(q)
    assert answer == "save.txt"
    assert no_clear(out.getvalue()) == 'Enter a filename:  Are you sure you want to overwrite junk.txt?  (y or n) Enter a filename:  Are you sure you want to overwrite save.txt?  (y or n) '
    set_inp(inp, "junk.txt\ny\nsave.txt\ny\n")
    reset(out)
    answer = p.ask(q)
    assert answer == 'junk.txt'
    assert no_clear(out.getvalue()) == 'Enter a filename:  Are you sure you want to overwrite junk.txt?  (y or n) '

def test_limit():
    inp = sio("1233\b456")
    p = pyline.pyline.PyLine(inp=inp)
    q = pyline.question.Question("Keep it brief: ", limit=5)
    ans = p.ask(q)
    assert ans == '12345'

def test_defaults():
    inp = sio("\nNo Comment\n")
    regans = pyline.answers.RegularAnswer("^y(?:es)|no?|no comment$", re.I)
    q = pyline.question.Question("Are you sexually active?  ", regans)
    p = pyline.pyline.PyLine(inp=inp)
    ans = p.ask(q)
    assert ans == 'No Comment'
    set_inp(inp, "\nYes\n")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    q = pyline.question.Question("Are you sexually active?  ", regans, default='No Comment')
    ans = p.ask(q)
    assert ans == 'No Comment'
    assert no_clear(out.getvalue()) == 'Are you sexually active?  |No Comment|  '
    ans = p.ask(q)
    assert ans == 'Yes'

def test_empty():
    inp = sio("\n\n")
    q = pyline.question.Question("", pyline.answers.RegularAnswer("^y(:es)?|no?$", re.I),
                                 default="yes")
    p = pyline.pyline.PyLine(inp=inp)
    ans = p.ask(q)
    assert ans == 'yes'

def test_gather():
    inp = sio("Bob\nCarol\nTed\nAlice\n\n")
    p = pyline.pyline.PyLine(inp=inp)
    q = pyline.question.Question("Enter four names: ", gather=4)
    ans = p.ask(q)
    assert ans == ['Bob','Carol','Ted','Alice']
    last = inp.readline()
    assert last == '\n'
    inp.seek(0)
    q.gather = ''
    ans = p.ask(q)
    assert ans == ['Bob', 'Carol', 'Ted', 'Alice']
    last = inp.readline()
    assert last == ''
    set_inp(inp, "29\n30\n49")
    out = sio()
    p = pyline.pyline.PyLine(out=out,inp=inp)
    q = pyline.question.Question("{key}:  ", int,
                                 gather=["Age","Wife's Age","Father's Age"])
    ans = p.ask(q)
    assert ans == {"Age":29, "Father's Age": 49, "Wife's Age": 30}
    assert no_clear(out.getvalue()) == "Age:  Wife's Age:  Father's Age:  "

def test_listdisplay():
    p = pyline.pyline.PyLine()
    digits = "one two three four five {0.blue:six} seven eight nine ten".split()
    from pyline import listdisplay as ld
    lines = p.listdisplay(digits)
    assert no_clear(lines) == 'one\ntwo\nthree\nfour\nfive\n\x1b[34msix\nseven\neight\nnine\nten'
    coldown = p.listdisplay(digits, ld.columns_down)
    assert no_clear(coldown) == 'one        three      five       seven      nine     \ntwo        four       \x1b[34msix        eight      ten      '
    colacross = p.listdisplay(digits, ld.columns_across, 3)
    assert no_clear(colacross) == '''\
one        two        three    \n\
four       five       \x1b[34msix      \n\
seven      eight      nine     \n\
ten      '''
    inline = p.listdisplay(digits, ld.inline, "; ")
    assert no_clear(inline) == 'one; two; three; four; five; \x1b[34msix; seven; eight; nine; or ten'
    twenty = ['12345678901234567890'] * 5
    assert no_clear(p.listdisplay(twenty, ld.columns_across)) == '12345678901234567890      12345678901234567890      12345678901234567890    \n12345678901234567890      12345678901234567890    '

