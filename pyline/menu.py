import itertools, string
import pyline
from .question import Question
from .answers import *
from .listdisplay import *
from .utils import *

INDEX, NAME, INDEX_OR_NAME = range(3)

class MenuError(Exception): pass

class Layout(object):
    def __init__(self, flow=None, flowoption=None):
        self.flow = flow or rows
        self.flowoption = flowoption
    
class OneLine(Layout):
    def __init__(self, flow=None, flowoption=None):
        Layout.__init__(self, flow or inline, flowoption)
    def __call__(self, menu):
        r = [menu.header+":  " if menu.header else '']
        r.append(menu.prompt)
        _, ws = remove_capture_whitespace(menu.prompt)
        r.append("(%s)" % \
                 menu.pyline.listdisplay(list(menu), self.flow, self.flowoption))
        r.append(ws)
        return ''.join(r)
class List(Layout):
    def __call__(self, menu):
        r = [menu.header+":\n" if menu.header else '']
        r.append(menu.pyline.listdisplay(list(menu), self.flow, self.flowoption))
        r.append('\n')
        r.append(menu.prompt)
        return ''.join(r)
class MenuOnly(Layout):
    def __init__(self, flow=None, flowoption=None):
        Layout.__init__(self, flow or inline, flowoption)
    def __call__(self, menu):
        return menu.pyline.listdisplay(list(menu), self.flow, self.flowoption) +\
                        menu.prompt

class Menu(Question):
    def __init__(self, items=None, hidden=None, index=None,
                 index_suffix=". ",
                 select_by=INDEX_OR_NAME,
                 header='', prompt='? ', layout=List(), shell=False,
                 none_on_handled=False, responses=None, pyline=None, **k):
        Question.__init__(self, prompt, MenuAnswer(self), **k)
        self.items = []
        self.hidden = []
        for i in items or []:
            self.add_choice(i)
        for i in hidden or []:
            self.add_hidden(i)
        self.index = index or number
        self.index_suffix = index_suffix
        self.select_by = select_by
        self.header = header
        self.prompt = prompt
        self.layout = layout
        self.shell = shell
        has_help = False
        self.has_help_help = has_help_help = False
        for i in itertools.chain(self.items, self.hidden):
            if i.help:
                has_help = True
                if i.name == 'help':
                    has_help_help = True
                    break
        if has_help and not has_help_help:
            self.items.append(MenuChoice('help',
                                         action=self.choose_help,
                                         help=self.__class__.default_help))
            self.has_help_help = True
        self.none_on_handled = none_on_handled
        self.responses.update(responses or {}) # set in Question.__init__
        self.pyline = pyline

    def add_choice(self, choice):
        if isinstance(choice, tuple):
            choice = MenuChoice(*choice)
        elif not isinstance(choice, MenuChoice):
            choice = MenuChoice(choice)
        if self.items and self.items[-1].name == 'help':
            h = self.items.pop()
            self.items.append(choice)
            self.items.append(h)
        else:
            self.items.append(choice)
        if choice.help and not self.has_help_help:
            if choice.name != 'help':
                self.items.append(MenuChoice('help',
                                  action=self.choose_help,
                                  help=self.__class__.default_help))
            self.has_help_help = True
    def add_choices(self, names, action):
        [self.choice(MenuChoice(name, action)) for name in names]
    def add_hidden(self, choice):
        with reassigning(self, "items", self.hidden):
            self.choice(choice)
    def add_hiddens(self, names, action):
        with reassigning(self, "items", self.hidden):
            self.choices(names, action)

    def options(self):
        allitems = self.items + self.hidden
        if self.index not in (Menu._index_none, Menu._index_const_str):
            by_index = [ChoiceProxy(i, e) for (i,e) in zip(self.index(self),
                                                          self.items)]
        else:
            by_index = []
        if self.select_by == NAME or self.shell:
            return allitems
        elif self.select_by == INDEX:
            return by_index
        return by_index + allitems

    def choose_help(self, *a):
        line = a[1].strip()
        res = self.items[-1] if self.items[-1].name == 'help' else self.hidden[-1]
        if line:
            with reassigning(self, 'answer', MenuHelpAnswer(self)):
                try:
                    self.convert(line)
                except (AmbiguousAutoCompleteMatch, NoAutoCompleteMatch):
                    res = None
                else:
                    res = self.answer.result
        if not res:
            self.pyline.say("There's no help for that topic.")
        elif hasattr(res.help, '__call__'):
            return res.help(self, line)
        else:
            self.pyline.say("= %s\n\n%s" % (res, res.help))

    def helptopics(self):
        with reassignings(self, ("index","select_by"), (noindex,NAME)):
            return list(c for c in self.options() if c.help)

    def default_help(self):
        self.pyline.say('This command will display helpful messages about '\
'functionality, like this one. To see the help for a specific topic '\
'enter:\n\thelp [TOPIC]\nTry asking for help on any of the following:\n\n%s\n'%\
self.pyline.listdisplay(self.helptopics(), columns_across))

    def selected(self, choice):
        if isinstance(choice, tuple): # shell or help
            choice, args = choice
            r = choice(args)
        else:
            r = choice()
        if self.none_on_handled:
            return None
        return r

    def winnow(self, candidates, answergiven):
        if self.shell or answergiven.startswith('help '):
            answergiven = answergiven.split(' ')[0]
        return Question.winnow(self, candidates, answergiven)

    def _get_index(self):
        return self._index

    def _set_index(self, idx):
        if not idx: idx = None
        if isinstance(idx, str):
            self.idxstr = idx
            self.index = Menu._index_const_str
            self.select_by = NAME
            self.index_suffix = ' '
        elif idx is None or idx is noindex:
            self._index = Menu._index_none
            self.select_by = NAME
        else:
            self._index = idx
    index = property(_get_index, _set_index)

    def _index_number(self):
        for i in range(len(self.items)):
            yield i+1
    def _index_letter(self):
        for (c,e) in zip(string.lowercase+string.uppercase, self.items):
            yield c
    def _index_none(self):
        return ('' for i in self.items)
    def _index_const_str(self):
        assert self.idxstr
        return (self.idxstr for i in self.items)

    def __iter__(self):
        for (prefix,i) in zip(self.index(self), self.items):
            suffix = self.index_suffix if prefix else ''
            yield "%s%s%s" % (prefix,suffix,self.pyline.effectize_string(str(i)))
    
    def __str__(self):
        if hasattr(self.layout, "__call__"):
            return self.layout(self)
        return str(self.layout)
            
number = Menu._index_number
letter = Menu._index_letter
noindex = Menu._index_none

class ChoiceProxy(object):
    def __init__(self, i, obj):
        self.i = str(i)
        self.obj = obj
    def __str__(self): return self.i
    def __call__(self, *a): return self.obj(*a)
    def __getattribute__(self, k):
        if k not in ('i', 'obj', '__str__'):
            return getattr(self.obj, k)
        return object.__getattribute__(self, k)
    

class MenuChoice(object):
    def __init__(self, name, action=None, help=''):
        self.name = name
        self.help = help
        self.action = action
    def __str__(self):
        return self.name
    def __call__(self, *rest):
        if not self.action:
            return self.name
        return self.action(*((self.name,)+rest))
