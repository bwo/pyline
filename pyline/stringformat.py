import re

'''
This module exposes a class (FormatString) and a function (fmt) that
mimic the built-in format() method of str and unicode objects. It
differs from it in some respects, however. It also differs from the
documentation in some respects (presently), though it conforms more
closely to the documentation than the implementation does.

For examples of the ways in which the implementation deviates from the
documentation (and arguably from the PEP which the implementation is
supposed to implment), see this bug report:
<http://bugs.python.org/issue12014> and this python-dev thread:
<http://mail.python.org/pipermail/python-dev/2011-June/111860.html>.

The deviations are relevant here because the PyLine intends to enable
its users to colorize output using constructs such as "This should be
{e.red[colored red!]}", but as currently implemented, str.format()
will reject that string, raising a ValueError.
'''

bracepat = re.compile("({{)|({)")
convmap = {'s':str,
           'r':repr}

period = ord('.')
lbrack = ord('[')
excl = ord('!')
colon = ord(':')

replacementdelim = re.compile('}')
elementindexdelim = re.compile("]")
namedelim = re.compile("[.!:}[]")


def get_last_brace(s, i, lowerlim):
    count = 0
    try:
        while count != 1 and count != lowerlim:
            if s[i] == '}': count += 1
            elif s[i] == '{': count -= 1
            i += 1
        if count == lowerlim: raise ValueError("Max string recursion exceeded")
    except IndexError:
        raise ValueError("unmatched '{' in format string")
    return i-1

def get_thing(pat, errmsg):
    def get(s, i):
        res = pat.search(s,i)
        if not res:
            raise ValueError(errmsg)
        beg, end = res.span()
        return s[i:beg], beg
    return get
get_name = get_thing(namedelim, "unmatched '{' in format string")
get_element_index = get_thing(elementindexdelim, "Missing ']' in format string")
get_format = get_thing(replacementdelim, "unmatched '{' in format string")

class FormatString(object):
    def __init__(self, s):
        self.number_from = 0
        self.auto_numbering_ok = True
        self.parsed = self.parse_replacement(s, 0, True)
    def format(self, *a, **k):
        return self.do_format(self.parsed, a, k)  
    def do_format(self, es, a, k):
        res = []
        for e in es:
            if not isinstance(e, tuple):
                res.append(e)
                continue
            field, conv, formatspec = e
            if isinstance(field[0], int):
                o = a[field[0]]
            else:
                o = k[field[0]]
            for f in field[1:]:
                o = f(o)
            if conv: o = convmap[conv](o)
            formatspec = self.do_format(formatspec, a, k)
            if not hasattr(o, '__format__'):
                res.append(object.__format__(o, formatspec))
            else:
                res.append(o.__format__(formatspec))
        return ''.join(res)            
    def parse_replacement(self, s, i, recurse):
        braces = list(bracepat.finditer(s))
        if not braces:
            return [do_escapes(s)]
        last = 0
        results = []
        for b in braces:
            beg, end = b.span()
            if last > beg: continue
            if b.group(1):
                results.append(do_escapes(s[last:end-1]))
                last = end
            else:
                results.append(do_escapes(s[last:beg]))
                last, substituend = self.extract_replacements(s, end, recurse)
                results.append(substituend)
        results.append(do_escapes(s[last:]))
        return results
    def extract_replacements(self, s, i, recurse):
        arg_name, i = get_name(s,i)
        if not arg_name:
            if not self.auto_numbering_ok:
                raise ValueError("cannot switch from automatic field numbering to manual field specification")
            field_name = [self.number_from]
            self.number_from += 1
        else:
            try:
                arg_name = int(arg_name)
            except:
                pass
            else:
                if self.number_from:
                    raise ValueError("cannot switch from automatic field numbering to manual field specification")
                self.auto_numbering_ok = False
            field_name = [arg_name]
        conv = None
        format = ''
        while True:
            os = ord(s[i])
            if os is period:
                attrname, i = get_name(s, i+1)
                if not attrname: raise ValueError, "Empty attribute in format string"
                field_name.append(lambda o, a=attrname: getattr(o, a))
                continue
            if os is lbrack:
                element_index, i = get_element_index(s, i+1)
                i += 1
                try:
                    element_index = int(element_index)
                except:
                    pass
                field_name.append(lambda o, e=element_index: o[e])
                continue
            break
        if os is excl:
            conv = s[i+1]
            i += 2
            if conv not in 'rs':
                raise ValueError("Unknown conversion specifier "+conv)
            os = ord(s[i])
        inc = 0
        if os is colon:
            i += 1
            lastbrace = get_last_brace(s, i, -2 if recurse else -1)
            format = self.parse_replacement(s[i:lastbrace], i, False)
            inc = lastbrace - i
        return 1+i+inc, (field_name, conv, format)

def do_escapes(s):
    i = 0
    m = len(s)
    while i < m:
        if s[i] == '}':
            if i + 1 == m or s[i+1] != '}':
                raise ValueError("Single '}' found in format string")
            i += 1
        i += 1
    return s.replace('}}','}')

def fmt(s, *a, **k):
    c = fmt.cache.get(s)
    if not c:
        c = FormatString(s)
        fmt.cache[s] = c
    return c.format(*a, **k)
fmt.cache = {}
