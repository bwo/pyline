"""Main interface to PyLine.
"""
import sys
import textwrap
import readline
from . import question
from . import colors
from .system import *
from .listdisplay import *
from .answers import *
from . import answers
from . import utils
from .menu import *
from . import menu
from .gather import gather_dispatch

def get_completer():
    return readline.get_completer()
def clear_completer():
    readline.set_completer()
def set_completer(choices):
    choices = sorted(map(str,choices))
    def completer(txt, state):
        if state == 0:
            completer.options = [c for c in choices if c.startswith(txt)]
        if state < len(completer.options):
            return completer.options[state]
        return None
    readline.set_completer(completer)


class PyLine(object):
    """Interact with the user over the console.

    All arguments to the constructor have sensible defaults:

    * out: File-like object for output.
    * inp: File-like object for input. 
    * wrap_at: column number at which to wrap lines. 
    * page_at: row number at which to prompt the user to page output. (Default: number of rows - 2)
    * colors: True if output should be colorized, False otherwise. 
    * colorscheme: custom :py:class:`ColorScheme` to use in colorizing output, or ``None`` to use the default. 

    If :py:func:`out.isatty` returns ``True``, we attempt to determine the actual terminal size; otherwise, 80 columns and 24 rows are assumed.

    """
    def __init__(self, out=None, inp=None, wrap_at=None,
                 page_at=None, colors=True, colorscheme=None):
        self.wrap_at = wrap_at
        self.out = out or sys.stdout
        self.inp = inp or sys.stdin
        self.colors = colors# if self.inp.isatty() else False
        self.cols, self.rows = self.dimensions()
        self.colorscheme = colorscheme
        self.page_at = page_at or self.rows - 2
        self.wrap_at = wrap_at or self.cols

    def dimensions(self):
        if self.out.isatty():
            return terminal_size()
        return (80, 24)

    def y_or_n_style_q(self, prompt, acceptable_answers):
        """Ask the user a question, with nonblocking input, no echoing, selecting one of a set of answers. The question is repeated on erroneous input.

        :param prompt: text of question
        :param acceptable_answers: sequence containing acceptable answers to the question.
        :rtype: the answer selected.

        Note that since only one character is read, no two answers should begin with the same character: it will be impossible for the user to select either of them, since the input read will always be ambiguous.

        This function is named after emacs' ``y-or-n-p``.
        """
        ans = answers.Choice(acceptable_answers)
        q = question.Question(prompt, ans, character=True,
                              ask_on_error=question.repeat_question)
        return self.ask(question=q, answer=ans)

    def yes_or_no_style_q(self, prompt, acceptable_answers):
        """Ask the user a question, selecting one of a set of answers.

        :param prompt: text of question
        :param acceptable_answers: sequence containing acceptable answers to the question.
        :rtype: the answer selected.

        Unlike :py:meth:`y_or_n_style_q`, the question will not be repeated on invalid input.

        This function is named after emacs' ``yes-or-no-p``.
        """
        ans = answers.Choice(acceptable_answers)
        q = question.Question(prompt, ans)
        return self.ask(question=q, answer=ans)

    def agree(self, prompt, character=False, default=None):
        """Ask the user a yes-or-no question.

        :param prompt: text of question
        :param character: ``True`` to use nonblocking input, ``False`` otherwise.
        :param default: default answer. 
        :rtype: ``True`` if the user agrees, ``False`` otherwise.

        See :py:class:`AgreeAnswer` for the acceptable answers.
        """
        p = utils.insert_before_whitespace(prompt, "  (y or n)")
        ans = answers.AgreeAnswer()
        q = question.Question(p, ans,
                              ask_on_error=p,
                              case=question.downcase,
                              character=character,
                              default=default)
        return self.ask(question=q, answer=ans)
    def y_or_n_q(self, prompt):
        """Alias for ``agree(prompt, character=True)``
        """
        return self.agree(prompt, True)
    def yes_or_no_q(self, prompt):
        """Alias for ``yes_or_no_style_p(prompt, ["yes", "no"])``
        """
        p = utils.insert_before_whitespace(prompt, " (yes or no)")
        return self.yes_or_no_style_q(p, ["yes","no"]) == 'yes'

    def say(self, s, *vals, **keys):
        s = str(s)
        if not s: return
        s = self.effectize_string(s, vals, keys)
        s, ws = utils.remove_capture_whitespace(s)
        lines = s.split('\n')
        lines = ['\n'.join(textwrap.wrap(s, self.wrap_at)) for s in lines]
        remaining = self.page(lines)
        remaining = '\n'.join(remaining)+ws
        self.out.write(remaining)
        if remaining[-1] not in '\t ':
            self.out.write('\n')
        self.out.flush()

    def no_colors(self):
        """
Context manager: on entry, output will no longer be colorized. ::
        
    p = pyline.PyLine(colors=True, ...)
    [...]
    with p.no_colors():
        p.say("{__colors.red:this will not be colorized}")
    p.say("{__colors.red:this will be red}")
    

"""
        return utils.reassigning(self, "colors", False)

    def effectize_string(self, s, vals=None, keys=None):
        keys = keys or {}
        vals = vals or ()
        return utils.effectize_string(s, vals, keys, self.colorscheme if self.colors else colors.none)

    def ask(self, question=None, prompt=None, answer=None, **k):
        """The most general method for asking a question.

        :param question: Question to ask.
        :param prompt: Prompt used to create a :py:class:`Question` if none is supplied.
        :param answer: Answer object used to create a :py:class:`Question` if none is supplied. If None or not supplied, :py:class:`Answer` will be used.
        :param k: keyword args passed to :py:class:`Question` constructor.
        :returns: the user's answer.
        
"""
        q = self._prep_question(question, prompt, answer, **k)
        if q.gather is not False:
            return self.do_gather(q)
        self._say_question(q)
        return self._answer_question(q)

    def _say_question(self, q):
        self.say(str(q))
        
    def _prep_question(self, question, prompt, answer, **k):
        if not answer: answer = Answer()
        if not question:
            q = Question(prompt, answer, **k)
        else: q = question
        return q

    def _answer_question(self, q):
        while 1:
            answer = self.get_response(q)
            answer = q.answer_or_default(answer)
            try:
                ans = q.convert(answer)
            except BadAnswer, e:
                handler = utils.get_by_class(e, q.responses)
                if not handler:
                    raise
                self.say(handler(e))
                q.explain_error(self)
                continue
            if q.confirm:
                if q.confirm is True:
                    confirmprompt = "Are you sure?  "
                else:
                    confirmprompt = q.confirm(ans)
                if not self.agree(prompt=confirmprompt):
                    q.explain_error(self)
                    continue
            return ans
#            return q.answer.result

    def get_response(self, q):
        if q.first_answer:
            return q.get_first_answer()
        if not q.character:
            if q.echo == True and not q.limit:
                return self.get_line(q)
            line = []
            line_length = 0
            while 1:
                ch = get_character(self.inp)
                if not ch:
                    raise EOFError
                o = ord(ch)
                if o in (10,13): break
                if not (o == 127 or o == 8):
                    line.append(ch)
                    line_length += 1
                    if q.echo == True:
                        self.out.write(ch)
                    elif q.echo != False:
                        self.out.write(q.echo)
                else:
                    if line_length:
                        if q.echo:
                            self.out.write(utils.effectize_string("\b{0.erase_char}"))
                        line_length -= 1
                        line.pop()
                if q.limit and line_length == q.limit:
                    break
                self.out.flush()
            if q.overwrite:
                self.out.write(utils.effectize_string("\r{0.erase_line}"))
                self.out.flush()
            else: self.out.write('\n')
            return ''.join(line)
        elif q.character == question.getc:
            return question.getc(self.inp)
        else:
            response = get_character(self.inp)
            if not response:
                raise EOFError
            if q.overwrite:
                self.out.write(utils.effectize_string("\r{0.erase_line}"))
                self.out.flush()
            else:
                if q.echo == True:
                    self.out.write(response)
                elif q.echo != False:
                    self.out.write(q.echo)
            return q.case(response)                            

    def get_line(self, q=None):
        ## uncertain about python's readline module: ignore it for now.
        if self.inp == sys.stdin:
            set_here = False
            if q:
                cands = q.answer.get_candidates()
                if cands and not get_completer():
                    set_here = True
                    set_completer(map(str,cands))
            line = raw_input()
            if set_here:
                clear_completer()
            return line
        else:
            line = self.inp.readline()
            if not line: raise EOFError
            return line

    def choose(self, *items_or_menu, **k):
        """Make a choice from a menu.

        If one positional argument is passed and it is an instance of :py:class:`Menu`, it is used as the menu object. Otherwise it is assumed that all positional arguments are either instance of :py:class:`MenuChoice` or tuples that can be passed to its constructor; in this case a :py:class:`Menu` object is constructed using the keyword arguments and the choices are added to it.

        :rtype: the user's choice.
"""
        if len(items_or_menu) == 1 and isinstance(items_or_menu[0], Menu):
            m = items_or_menu[0]
        else:
            m = Menu(**k)
            for i in items_or_menu:
                m.add_choice(i)
        m.pyline = self
        res = self.ask(question=m)
        return m.selected(res)

    def shell(self, *items_or_menu, **k):
        if len(items_or_menu) == 1 and isinstance(items_or_menu[0], Menu):
            m = items_or_menu[0]
        else:
            m = Menu(**k)
            for i in items_or_menu:
                m.add_choice(i)
        m.pyline = self
        res = self.ask(question=m)
        try:
            while True:
                m.selected(res)
                self.say(m.prompt)
                res = self._answer_question(m)
        except ShellExit:
            pass
            

    def listdisplay(self, items, mode=None, *args):
        """Format a list of items as a string for display.

        :param items: items to be displayed.
        :param mode: the way to display them. Defaults to :py:func:`rows`. See :py:mod:`listdisplay`.
        :param \*args: optional args to ``mode``. See :py:mod:`listdisplay`.
        :rtype: formatted string
"""
        if not items: return ''
        mode = mode or rows
        items = map(str, items)
        items = map(self.effectize_string, items)
        s = mode(self, items, *args)
        return s

    def page(self, lines):
        # this directly copies highline, but I think it's a mistake:
        # the what if lines is a multiple of page_at?
        size = len(lines)
        page_at = self.page_at
        while size > page_at:
            self.out.write('\n'.join(lines[:page_at]))
            lines = lines[page_at:]
            size -= page_at
            self.out.write('\n')
            c = self.y_or_n_style_q("-- press enter/return to continue or q to stop -- ", 'Qq\n')
            self.out.write('\n')
            if c in 'Qq':
                return ["...\n"]+lines[-2:]            
        return lines

    def do_gather(self, q):
        g = q.gather
        q.gather = False
        return gather_dispatch[type(g)](g, self, q)

    def install(self):
        '''insert aliases for say(), shell(), choose(), ask() and the other question-asking methods into the global namespace of the caller.
'''
        caller = sys._getframe(1)
        install_these = 'say shell choose ask agree y_or_n_style_q yes_or_no_style_q y_or_n_q yes_or_no_q'.split()
        for install_this in install_these:
            caller.f_globals[install_this] = getattr(self, install_this)
