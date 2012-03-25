import os
import pytest
import pyline.pyline
import pyline.listdisplay
import pyline.menu
from conftest import *

def test_layouts():
    inp = sio("1")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp, out=out)
    mitems = ("foo", "bar", "baz", "this one is longer")
    res = p.choose(*mitems, layout=pyline.menu.List(), header="pick one")
    v = no_clear(out.getvalue())
    assert v == '''\
pick one:
1. foo
2. bar
3. baz
4. this one is longer
? '''
    assert res == 'foo'
    set_inp(inp, '1')
    reset(out)
    res = p.choose(*mitems, layout=pyline.menu.List(flow=pyline.listdisplay.columns_down), header='pick one')
    v = no_clear(out.getvalue())
    assert v == '''\
pick one:
1. foo                     3. baz
2. bar                     4. this one is longer
? '''
    reset(out)
    set_inp(inp, '1')
    p.choose(*mitems, header='pick one', layout=pyline.menu.List(flow=pyline.listdisplay.columns_across))
    v = no_clear(out.getvalue())
    assert v == '''\
pick one:
1. foo                     2. bar                     3. baz
4. this one is longer
? '''
    reset(out)
    set_inp(inp,'1')
    p.choose(*mitems, header='pick one', layout=pyline.menu.List(flow=pyline.listdisplay.inline))
    v = no_clear(out.getvalue())
    assert v == '''\
pick one:
1. foo, 2. bar, 3. baz, or 4. this one is longer
? '''
    ## having established that the menu correctly does use the layout,
    ## we will not actually test each listdisplay option with each
    ## layout mode, preferring to establish that the listdisplay
    ## options function correctly elsewhere.

    reset(out)
    set_inp(inp,'1')
    p.choose(*mitems, header='pick one', layout=pyline.menu.MenuOnly())
    assert no_clear(out.getvalue()) == '''\
1. foo, 2. bar, 3. baz, or 4. this one is longer? '''
    reset(out)
    set_inp(inp,'1')
    p.choose(*mitems, header='pick one', layout=pyline.menu.MenuOnly(pyline.listdisplay.rows))
    assert no_clear(out.getvalue()) == '''\
1. foo
2. bar
3. baz
4. this one is longer? '''
    reset(out)
    set_inp(inp,'1')
    p.choose(*mitems, header='pick one', layout=pyline.menu.OneLine(), prompt='which do you prefer? ')
    assert no_clear(out.getvalue()) == '''\
pick one:  which do you prefer? (1. foo, 2. bar, 3. baz, or 4. this one is\nlonger) '''

def test_shell():
    inp = sio("double this please")
    out = sio()
    p = pyline.pyline.PyLine(inp=inp,out=out)
    items = [pyline.menu.MenuChoice(*t) for t in (
        ("double", lambda k,rest:rest+' '+rest),
        ("reverse", lambda k, rest: rest[::-1]),
        ("ls", lambda k, rest: os.listdir(os.path.split(__file__)[0])),
        )]
    m = pyline.menu.Menu(items, shell=True, header="look at these lovely choices", prompt="what to do> ")
    res = p.choose(m)
    assert res == "this please this please"
    reset(out)
    set_inp(inp, "ls")
    res = p.choose(m)
    assert os.path.split(__file__)[1] in res
