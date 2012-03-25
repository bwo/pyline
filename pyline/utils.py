import re, contextlib, textwrap
from .colors import e

def remove_capture_whitespace(s):
    m = re.search("([ \t\n]+)$", s)
    if not m:
        return (s, '')
    return (s[:m.start()], m.group(1))

def insert_before_whitespace(s, insert):
    s, ws = remove_capture_whitespace(s)
    if not s.endswith(insert):
        s += insert
    s += ws
    return s

def effectize_string(s, vals=None, keys=None, scheme=None):
    scheme = scheme or e
    keys = keys or {}
    vals = vals or ()
    s, ws = remove_capture_whitespace(s)
    if not s.endswith(e.clear.code):
        s = s.format(scheme, __colors=scheme, *vals, **keys)+e.clear.code + ws
    else: s += ws
    return s

unset = object()

def reassigning(obj, name, newobj):
    return reassignings(obj, [name], [newobj])

@contextlib.contextmanager
def reassignings(obj, names, newobjs):
    olds = [getattr(obj, name, unset) for name in names]
    [setattr(obj, name, newobj) for (name, newobj) in zip(names, newobjs)]
    try:
        yield
    finally:
        for (name, old) in zip(names, olds):
            if old is unset:
                delattr(obj, name)
            else:
                setattr(obj, name, old)

_escape_pat = re.compile('\033[^m]+?m')
def real_len(s):
    return len(_escape_pat.sub('', s))
textwrap.len = real_len #what base trickery!

def get_by_class(obj, dispatch):
    for k in obj.__class__.__mro__:
        if dispatch.has_key(k):
            return dispatch[k]
    return None

class NotAPrefix(Exception):
    pass
class NotAUniquePrefix(Exception):
    pass

class Trie:
    def __init__(self, items):
        self.out = {}
        self.hasbranches = False
        self.isterm = False
        for i in items:
            self.insert(str(i), i)
    def __contains__(self, word):
        trie = self
        for c in word:
            if c not in trie.out: return False
            trie = trie.out[c]
        return trie.isterm
    def insert(self, word, val):
        if word in self: return
        if self.out: self.hasbranches = True 
        trie = self
        i = 0
        while i < len(word) and word[i] in trie.out:
            trie = trie.out[word[i]]
            trie.hasbranches = True
            i += 1
        if i == len(word):
            trie.isterm = True
            return
        trie.out[word[i]] = Trie([word[i+1:]])
        while i < len(word):
            trie = trie.out[word[i]]
            i += 1
        trie.isterm = True
        trie.val = val
    def get_by_prefix(self, word):
        trie = self
        for c in word:
            if c not in trie.out:
                raise NotAPrefix
            trie = trie.out[c]
        if trie.hasbranches:
            raise NotAUniquePrefix
        while trie.out:
            for c in trie.out:
                trie = trie.out[c]
        return trie.val
    def get_all_by_prefix(self, word):
        trie = self
        w = []
        for c in word:
            if c not in trie.out:
                raise NotAPrefix
            w.append(c)
            trie = trie.out[c]
        w = ''.join(w)
        for rest in trie:
            yield w+rest
    def __iter__(self):
        if self.isterm: yield ''
        for c in self.out:
            for rest in self.out[c]:
                yield c+rest
