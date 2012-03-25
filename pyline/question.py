import re, sys
from . import system
from .answers import *
from .listdisplay import inline_simple
from .utils import remove_capture_whitespace, Trie, NotAPrefix, NotAUniquePrefix

character = system.get_character
getc = lambda inp: inp.read(1)

## whitespace manipulation
chomp = strip = str.strip
collapse = lambda s: re.sub("\s+"," ", s)
chomp_and_collapse = strip_and_collapse = lambda s: collapse(strip(s))
remove = lambda s: re.sub("\s+", "", s)

#case manipulation
up = upcase = str.upper
down = downcase = str.lower
capitalize = str.capitalize

#non manipulation
identity = preserve = lambda s: s

def pathnames(sofar, glob):
    [os.path.basename(f) for f in glob.glob(os.path.join(sofar+glob))]

class Question(object):
    def __init__(self, prompt, answer=None, character=None, limit=None,
                 echo=None, readline=False, whitespace=strip, default=None,
                 case=preserve, confirm=None, gather=False, first_answer=None,
                 responses=None, overwrite=False, ask_on_error="? "):
        self.prompt = prompt
        if not answer or answer is str:
            answer = Answer()
        elif isinstance(answer, (tuple, list)):
            answer = Choice(answer)
        elif answer is int:
            answer = IntAnswer()
        elif answer is float:
            answer = FloatAnswer()
        elif answer is file:
            answer = File()
        self.answer = answer
        self.answer.question = self
        self.character = character        
        self.limit = limit
        if echo is None:
            echo = not character
        self.echo = echo
        self.ask_on_error = ask_on_error
        self.readline = readline
        self.whitespace = whitespace
        self.default = default
        self.case = case
        self.confirm = confirm
        self.gather = gather
        self.first_answer = first_answer
        self.responses = question_error_dispatch
        self.responses.update(responses or {})
        self.overwrite = overwrite
        self.append_default()

    def __str__(self):
        return self.prompt

    def repeat_question(self, pyline):
        pyline.say(str(self))

    def winnow(self, candidates, answergiven):
        t = Trie(candidates)
        try:
            return t.get_by_prefix(answergiven)
        except NotAPrefix:
            raise NoAutoCompleteMatch
        except NotAUniquePrefix:
            raise AmbiguousAutoCompleteMatch, t.get_all_by_prefix(answergiven)

    def convert(self, ans):
        cands = self.answer.get_candidates()
        if cands == None:
            self.answer.convert(ans, ans)
        else:
            choice = self.winnow(cands, ans)
            self.answer.convert(choice, ans)

    def answer_or_default(self, ans):
        ans = self.case(self.whitespace(ans))
        if not ans and self.default is not None:
            return self.default
        else:
            return ans

    def explain_error(self, pyline):
        if hasattr(self.ask_on_error, '__call__'):
            self.ask_on_error(self, pyline)
        elif self.ask_on_error:
            pyline.say(self.ask_on_error)

    def get_first_answer(self):
        try:
            return self.first_answer
        finally:
            self.first_answer = None    

    def append_default(self):
        if not self.default: return
        prompt = self.prompt
        if not prompt:
            self.prompt = "|%s|  " % self.default
        elif prompt[-1] == "\n":
            self.prompt = prompt[:-1]+ ("  |%s|\n" % self.default)
        elif prompt == "":
            self.prompt = "|%s|  " % self.default
        else:
            q, ws = remove_capture_whitespace(prompt)
            self.prompt = "%s  |%s|%s" % (q,self.default,ws)
    
repeat_question = Question.repeat_question
