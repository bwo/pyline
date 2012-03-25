import os
import pytest
import pyline.pyline
import pyline.question
import pyline.answers
from conftest import *

def test_pathname_answer(tmpdir):
    tmpdir.mkdir('sub').ensure(dir=True)
    tmpdir.mkdir('anothersub').ensure(dir=True)
    tmpdir.join('foo.txt').ensure()    
    tmpdir.join('bar.ext').ensure()
    tmpdir.join('baz.ext').ensure()
    a = pyline.answers.Pathname(directory=tmpdir.strpath)
    assert a.get_candidates() == [p.basename for p in tmpdir.listdir()]
    inp = sio("foo\n")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    res = p.ask(pyline.question.Question("Select a file: ", a))
    assert res == os.path.join(tmpdir.strpath, 'foo.txt')
    set_inp(inp, "ano")
    res = p.ask(pyline.question.Question("Select a file: ", a))
    assert res == os.path.join(tmpdir.strpath, "anothersub")
    a.glob = '*.ext'
    reset(out)
    set_inp(inp, 'foo\nbaz\n')
    ans = p.ask(pyline.question.Question("Select a file: ", a))
    assert ans == os.path.join(tmpdir.strpath, 'baz.ext')
    assert no_clear(out.getvalue()) == 'Select a file: No match for that input\n? '

def test_file_answer(tmpdir):
    tmpdir.join("foo.txt").ensure()
    tmpdir.join("bar.txt").write("hi")
    tmpdir.join("baz.txt").ensure()
    a = pyline.answers.File(directory=tmpdir.strpath)
    assert a.get_candidates() == [p.basename for p in tmpdir.listdir()]
    inp = sio("bar\n")
    p = pyline.pyline.PyLine(inp=inp)
    q = pyline.question.Question("Select a file: ", a)
    res = p.ask(q)
    assert isinstance(res, file)
    assert res.read() == 'hi'
    res.close()
    a = pyline.answers.File(directory=tmpdir.strpath, mode="w")
    assert a.get_candidates() is None
    q.answer = a
    set_inp(inp, "newfile.txt\n")
    assert len(tmpdir.listdir()) == 3
    res = p.ask(q)
    assert len(tmpdir.listdir()) == 4
    assert res.mode == 'w'
    res.close()
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    set_inp(inp, "../sneaky")
    with pytest.raises(EOFError):
        p.ask(q)
    assert no_clear(out.getvalue()) == 'Select a file: Answer could not be processed: Cannot enter parent directory\n? '

def test_callable_answer():
    class Name:
        def __init__(self, s):
            try:
                last, rest = s.split(', ')
                first, middle = rest.split(' ')
            except ValueError:
                raise pyline.answers.BadAnswer("Invalid name format.")
            self.first = first
            self.middle = middle
            self.last = last
    a = pyline.answers.Callable(Name)
    q = pyline.question.Question("Your name? ", a)
    inp = sio("Doe, John Edward\n")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    res = p.ask(q)
    assert isinstance(res, Name)
    assert res.last == 'Doe'
    assert res.middle == 'Edward'
    assert res.first == 'John'
    reset(out)
    set_inp(inp, "Doe, Doe, Doe!\n")
    with pytest.raises(EOFError):
        res = p.ask(q)
    assert no_clear(out.getvalue()) == 'Your name? Answer could not be processed: Invalid name format.\n? '
