import os, glob, re
from . import listdisplay
class BadAnswer(Exception):
    pass
class BadRange(BadAnswer):
    pass
class BadChoice(BadAnswer):
    pass
class BadType(BadAnswer):
    pass
class NoAutoCompleteMatch(BadAnswer):
    pass
class AmbiguousAutoCompleteMatch(BadAnswer):
    pass

class Answer(object):
    def get_candidates(self):
        return None
    def validate(self, result):
        return result
    def do_convert(self, chosen, entered):
        return chosen # trivial conversion
    def convert(self, chosen, entered):
        res = self.do_convert(chosen, entered)
        self.result = self.validate(res)

class Boundable(Answer):
    def __init__(self, below=None, above=None):
        self.below = below
        self.above = above
    def valid(self, result):
        return (not self.below or result < self.below) and \
               (not self.above or result > self.above)
    def validate(self, result):
        if not self.valid(result):
            raise BadRange, self.explain_bounds()
        return result
    def explain_bounds(self):
        e = []
        if self.below: e.append("below %s" % self.below)
        if self.above: e.append("above %s" % self.above)
        return " and ".join(e)

class RegularAnswer(Answer):
    def __init__(self, pat, flags):
        self.pat = re.compile(pat, flags)
    def validate(self, result):
        if not self.pat.match(result):
            raise BadAnswer
        return result

class SimpleConversion(Answer):
    def __init__(self, func, explanation):
        self.func = func
        self.explanation = explanation
    def do_convert(self, ans, entered):
        try:
            return self.func(ans)
        except (ValueError, TypeError):
            raise BadType, self.explanation

class IntAnswer(Boundable, SimpleConversion):
    def __init__(self, below=None, above=None):
        SimpleConversion.__init__(self, int, "You must enter a valid integer")
        Boundable.__init__(self, below, above)

class FloatAnswer(Boundable, SimpleConversion):
    def __init__(self, below=None, above=None):
        SimpleConversion__init__(self, float, "You must enter a floating-point number")
        Boundable.__init__(self, below, above)

class Choice(Answer):
    def __init__(self, choices):
        self.choices = choices
    def get_candidates(self):
        return self.choices
    def validate(self, result):
        if result not in self.choices:
            raise BadChoice, "answer must be one of %s" % \
                  listdisplay.inline_simple(self.choices, "; ")
        return result

class Pathname(Answer):
    def __init__(self, directory=None, glob="*"):
        self.directory = directory or os.getcwd()
        self.glob = glob
    def get_candidates(self):
        return [os.path.basename(f) for f in \
                glob.glob(os.path.join(self.directory,self.glob))]
    def validate(self, result):
        if not os.path.exists(result):
            raise BadAnswer, "File or directory does not exist."
        return result
    def do_convert(self, ans, entered):
        return os.path.join(self.directory, ans)

class File(Pathname):
    def __init__(self, directory=None, glob="*", mode="r"):
        Pathname.__init__(self, directory, glob)
        self.mode = mode
    def get_candidates(self):
        if self.mode in ("r", "rb", "r+", "rb+"):
            return [os.path.basename(f) for f in \
                    glob.glob(os.path.join(self.directory, self.glob)) if \
                    os.path.isfile(f)]
        return None
    def validate(self, result):
        return result # any failure will already be apparent in convert().
    def do_convert(self, ans, entered):
        ans = os.path.join(self.directory, ans)
        if not os.path.normpath(ans).startswith(self.directory):
            raise BadAnswer, "Cannot enter parent directory"
        try:
            return open(ans, self.mode)
        except IOError, e:
            raise BadAnswer, e.strerror

class Callable(Answer):
    def __init__(self, f, *a, **k):
        self.f = f
        self.a = a
        self.k = k
    def do_convert(self, ans, entered):
        return self.f(*((ans,)+self.a), **self.k)

class MenuAnswer(Answer):
    def __init__(self, menu):
        self.menu = menu
    def get_candidates(self):
        return self.menu.options()
    def do_convert(self, ans, entered):
        if self.menu.shell or ans.name == 'help':
            return (ans, ' '.join(entered.split(' ')[1:]))
        else:
            return ans

class AgreeAnswer(Answer):
    def validate(self, result):
        if not (result == 'y' or result == 'yes' or \
                result == 'n' or result == 'no'):
            if self.question.character:
                raise BadChoice, "Please answer y or n"
            raise BadChoice, "Please answer y, n, yes, or no"
        return result == 'y' or result == 'yes'

class MenuHelpAnswer(MenuAnswer):
    def get_candidates(self):
        return self.menu.helptopics()
    def do_convert(self, ans, entered):
        return ans

question_error_dispatch = {
        BadChoice: lambda e: str(e),
        BadType: lambda e: str(e),
        AmbiguousAutoCompleteMatch: lambda e: "Ambiguous match: could be any of %s" % listdisplay.inline_simple(map(str,e.args[0])).strip(),
        NoAutoCompleteMatch: lambda e: "No match for that input",
        BadRange: lambda e: "Your answer isn't within the expected range: %s" % e,
        BadAnswer: lambda e: "Answer could not be processed: %s" % e,
        }
