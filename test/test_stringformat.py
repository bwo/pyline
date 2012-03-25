### copying the tests from python's test suite (test_unicode:test_format) 
### not all of them, though, because many are highly redundant!
import pytest
import datetime
from pyline.stringformat import fmt

def test_simpleformat():
    assert fmt('') == ''
    assert fmt('a') == 'a'
    assert fmt('ab') == 'ab'
    assert fmt('a{{') == 'a{'
    assert fmt('a}}') == 'a}'
    assert fmt('{{b') == '{b'
    assert fmt('}}b') == '}b'
    assert fmt('a}}b') == 'a}b'
    

def test_arguments():
    assert fmt('My name is {0}', 'Fred') == 'My name is Fred'
    assert fmt('My name is {}', 'Fred') == 'My name is Fred'
    assert fmt('My name is {0[name]}', dict(name='Fred')) == 'My name is Fred'
    assert fmt('My name is {} :-{{}}', 'Fred') == 'My name is Fred :-{}'
    d = datetime.date(2007, 8, 18)
    assert fmt('The year is {0.year}', d) == 'The year is 2007'
    assert fmt('{0}', 'abc') == 'abc'
    assert fmt('{1}', 1, 'abc') == 'abc'
    assert fmt('X{1}', 1, 'abc') == 'Xabc'
    assert fmt('X{1}Y', 1, 'abc') == 'XabcY'
    assert fmt('{}', -15) == '-15'
    assert fmt('{{') == '{'
    assert fmt('{{x}}') == '{x}'
    assert fmt('{{{0}}}', 123) == '{123}'
    assert fmt('}}{{') == '}{'


class C:
    def __init__(self, x=100):
        self._x = x
    def __format__(self, spec):
        return spec
class D:
    def __init__(self, x):
        self.x = x
    def __format__(self, spec):
        return str(self.x)
class E:
    def __init__(self, x):
        self.x = x
    def __str__(self):
        return 'E('+self.x+')'
class F:
    def __init__(self, x):
        self.x = x
    def __repr__(self):
        return 'F('+self.x+')'

class G:
    def __init__(self, x):
        self.x = x
    def __str__(self):
        return "string is "+self.x
    def __format__(self, format_spec):
        if format_spec == 'd':
            return 'G('+self.x+')'
        return object.__format__(self, format_spec)
class I(datetime.date):
    def __format__(self, fspec):
        return self.strftime(fspec)
class J(int):
    def __format__(self, fspec):
        return int.__format__(self*2, fspec)

def test_weird_field_names():
    assert fmt('{0[foo-bar]}', {'foo-bar':'baz'}) == 'baz'
    assert fmt('{[foo bar]}', {'foo bar': 'baz'}) == 'baz'
    assert fmt('{[ ]}', {' ':3}) == '3'
    assert fmt('{0[{]}', {'{':3}) == '3'
    assert fmt('{0[!]}', {'!':3}) == '3'

def test_more_complex():
    assert fmt('{foo._x}', foo=C(20)) == '20'
    assert fmt('{1}{0}', D(10), D(20)) == '2010'
    assert fmt('{0._x.x}', C(D('abc'))) == 'abc'
    assert fmt('{0[0]}', ['abc', 'def']) == 'abc'
    assert fmt('{0[1]}', ['abc', 'def']) == 'def' 
    assert fmt('{0[1][0]}', ['abc', ['def']]) == 'def'
    assert fmt('{0[1][0].x}', ['abc', [D('def')]]) == 'def'

def test_strings():
    assert fmt('{0:.3s}', 'abc') == 'abc'
    assert fmt('{0:.3s}', 'ab') == 'ab'
    assert fmt('{0:.3s}', 'abcdef') == 'abc'
    assert fmt('{0:.0s}', 'abcdef') == ''
    assert fmt('{0:3.3s}', 'abc') == 'abc'
    assert fmt('{0:2.3s}', 'abc') == 'abc'
    assert fmt('{0:2.2s}', 'abc') == 'ab'
    assert fmt('{0:3.2s}', 'abc') == 'ab '
    assert fmt('{0:x<0s}', 'result') == 'result'
    assert fmt('{0:x<5s}', 'result') == 'result'
    assert fmt('{0:x<6s}', 'result') == 'result'
    assert fmt('{0:x<7s}', 'result') == 'resultx'
    assert fmt('{0:x<8s}', 'result') == 'resultxx'
    assert fmt('{0: <7s}', 'result') == 'result '
    assert fmt('{0:<7s}', 'result') == 'result '
    assert fmt('{0:>7s}', 'result') == ' result'
    assert fmt('{0:>8s}', 'result') == '  result'
    assert fmt('{0:^8s}', 'result') == ' result '
    assert fmt('{0:^9s}', 'result') == ' result  '
    assert fmt('{0:^10s}', 'result') == '  result  '
    assert fmt('{0:10000}', 'a') == 'a' + ' ' * 9999
    assert fmt('{0:10000}', '') == ' ' * 10000
    assert fmt('{0:10000000}', '') == ' ' * 10000000

    assert fmt('{0:abc}', C()) == 'abc'

def test_coercions():
    assert fmt('{0!s}', 'Hello') =='Hello'
    assert fmt('{0!s:}', 'Hello') =='Hello'
    assert fmt('{0!s:15}', 'Hello') =='Hello          '
    assert fmt('{0!s:15s}', 'Hello') =='Hello          '
    assert fmt('{0!r}', 'Hello') =="'Hello'"
    assert fmt('{0!r:}', 'Hello') =="'Hello'"
    assert fmt('{0!r}', F('Hello')) =='F(Hello)'
    assert fmt('{0!r}', '\u0378') == '{0!r}'.format('\u0378') # nonprintable
    assert fmt('{0!r}', '\u0374') == '{0!r}'.format('\u0374')  # printable
    assert fmt('{0!r}', F('\u0374')) =='F(\u0374)'
    try:
        '{0!a}'.format('1')
    except ValueError:
        pass
    else:
        assert fmt('{0!a}', 'Hello') =="'Hello'"
        assert fmt('{0!a}', '\u0378') =="'\\u0378'" # nonprintable
        assert fmt('{0!a}', '\u0374') =="'\\u0374'" # printable
        assert fmt('{0!a:}', 'Hello') =="'Hello'"
        assert fmt('{0!a}', F('Hello')) =='F(Hello)'
        assert fmt('{0!a}', F('\u0374')) =='F(\\u0374)'

def test_fallback():
    assert fmt('{0}', {}) == '{}'
    assert fmt('{0}', []) == '[]'
    assert fmt('{0}', [1]) == '[1]'

    assert fmt('{0:d}', G('data')) == 'G(data)'
    assert fmt('{0!s}', G('data')) == 'string is data'

    # we'll skip the warnings because they're dependent on python version
    # and underlying machinery that I'm not directly responsible for
    assert fmt('{0:^10}', E('data')) == ' E(data)  '
    assert fmt('{0:^10s}', E('data')) == ' E(data)  '
    assert fmt('{0:>15s}', G('data')) == ' string is data'

    assert fmt('{0:date: %Y-%m-%d}', I(year=2007,
                                       month=8,
                                       day=27)) == 'date: 2007-08-27'
    assert fmt("{0}", J(10)) == '20'

    assert fmt("{0:}", "a") == "a"

    assert fmt("{0:.{1}}", 'hello world', 5) == 'hello'
    assert fmt("{0:.{1}s}", "hello world", 5) == 'hello'
    assert fmt("{0:.{precision}s}", "hello world", precision=5) == 'hello'
    assert fmt("{0:{width}.{precision}s}", 'hello world', width=10, precision=5) == 'hello     '

def test_errors():
    for verror in '{', '}', 'a{', '}a', 'a}', '{a', '}{', '{0', \
                   "abc{0:{}", "{0[}":
        with pytest.raises(ValueError):
            fmt(verror)
    with pytest.raises(ValueError):
        fmt("{0.}", 0)
    for kerr in "{x}", "{0]}":
        with pytest.raises(KeyError):
            fmt(kerr)
    with pytest.raises(IndexError):
        fmt("{1}", "abc")
    for ierr in "{:}", "{:s}", "{}":
        with pytest.raises(IndexError):
            fmt(ierr)
            
    with pytest.raises(ValueError):
        fmt("{0:{1:{2}}}", 'abc', 's', '')

