import sys
import pytest
import pyline.pyline
import pyline.colors

def test_using_colors(capsys):
    p = pyline.pyline.PyLine(colors=True, out=sys.stdout)
    p.say("this should be {0.black:black}")
    out, err = capsys.readouterr()
    assert out == u"this should be \x1b[30mblack\x1b[0m\x1b[0m\n"
    with p.no_colors():
        p.say("this should be {0.black:uninterpreted}")
        out, err = capsys.readouterr()
        assert out == "this should be {0.black:uninterpreted}\n"
    p.say("colored {0.black.on_red.underline:again}")
    out, err = capsys.readouterr()
    assert out == "colored \x1b[30m\x1b[41m\x1b[4magain\x1b[0m\x1b[0m\n"
    with pytest.raises(AttributeError):
        p.say("There is no such color as {0.puce:puce}!")

def test_more_complex_formatting(capsys):
    p = pyline.pyline.PyLine(colors=True, out=sys.stdout)
    p.say("{0.red:hello}, {1}, how are {__colors.red:{you}}", "world", you="you")
    out, err = capsys.readouterr()
    assert out == "\x1b[31mhello\x1b[0m, world, how are \x1b[31myou\x1b[0m\x1b[0m\n"

def test_colorscheme(capsys):
    cs = pyline.colors.ColorScheme(badwarning="yellow on_black",
                                   happiness=("blue", "bold", "underline"))
    p = pyline.pyline.PyLine(colors=True, colorscheme=cs, out=sys.stdout)
    p.say("{0.badwarning.blink:danger will robinson}")
    p.say("{0.happiness:it's ok after all}")
    out, err = capsys.readouterr()
    assert out == "\x1b[33m\x1b[40m\x1b[5mdanger will robinson\x1b[0m\x1b[0m\n\x1b[34m\x1b[1m\x1b[4mit's ok after all\x1b[0m\x1b[0m\n"
    with pytest.raises(AttributeError):
        p.say("{0.undefined:404}")
