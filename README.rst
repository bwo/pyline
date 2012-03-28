PyLine
======

**PyLine** is a Python rewrite/reinterpretation of the Ruby CLI library HighLine_.

.. _HighLine: http://highline.rubyforge.org/doc/

It supports colored output, user interaction (via simple questions or
complex menus), auto-paged, column-wrapped output, and almost no
documentation at the moment.

But it does have some examples! Look:

Examples
--------

Colorized text::

    >>> p = PyLine(colors=True)
    >>> p.say("Hello, {__colors.green.on_blue.bold:{1} world}!", "colorful")
    Hello, colorful world! # (but "colorful world" is in bold, green text on a blue background, see. That's the point.)
    >>> with p.no_colors():
        p.say("Hello, {__colors.green.on_blue.bold:{1} world}!", "drab")
    Hello, drab world! # (not colorized)

Simple questions::

    >>> answer = p.agree("Neat, huh? ")
    Neat, huh?  (y or n) q
    Please answer y, n, yes, or no
    Neat, huh?  (y or n) y
    >>> answer
    True
    >>> q = Question(prompt="Enter a sekrit number between 4 and 23 (exclusive): ", answer=IntAnswer(below=23, above=4), echo="*", ask_on_error="do it right: ")
    >>> ans = p.ask(q)
    Enter a sekrit number between 4 and 23 (exclusive): **
    Your answer isn't within the expected range: below 23 and above 4
    do it right: * 
    Your answer isn't within the expected range: below 23 and above 4
    do it right: *
    >>> ans
    9
    >>> q = Question(prompt="What's your favorite configuration file? ", answer=Pathname(directory="/etc", glob="*.conf"), default="logrotate.conf")
    >>> p.ask(q)
    What's your favorite configuration file?  |logrotate.conf| 
    '/etc/logrotate.conf'
    >>> p.ask(q)
    What's your favorite configuration file?  |logrotate.conf| n
    Ambiguous match: could be any of nscd.conf, nsswitch.conf, or ntp.conf
    ? nscd
    '/etc/nscd.conf'
    >>> q = Question("What's your favorite language? ", answer="perl python ruby".split(), confirm=True)
    >>> p.ask(q)
    What's your favorite language? perl
    Are you sure?  (y or n) y
    'perl'

More complex questions::

    >>> m = Menu(header="another way to choose your fav", prompt="-> ")
    >>> m.add_choices("perl python ruby".split(), None)
    >>> m.add_hidden(MenuChoice("haskell"))
    >>> p.choose(m)
    another way to choose your fav:
    1. perl
    2. python
    3. ruby
    -> haskell
    'haskell'
    >>> m.select_by = INDEX
    >>> m.layout = MenuOnly()
    >>> p.wrap_at = 20
    >>> p.choose(m)
    1. perl, 2. python,
    or 3. ruby
    -> 2
    'python'
    >>> q = Question(prompt="what is your favorite {key}? ", gather=["animal", "color", "food"])
    >>> ans = p.ask(q)
    what is your favorite animal? bear
    what is your favorite color? blue
    what is your favorite food? berry
    >>> ans
    {'color': 'blue', 'food': 'berry', 'animal': 'bear'}


Menus can also act as *shells*, associating each choice with a function to be called with the rest of the line::

    >>> m = Menu(header="perform stupid string tricks", items=[("reverse", lambda opt, mn, line: mn.pyline.say(line[::-1]), "reverse the string"), ("upcase", lambda opt, mn, line: mn.pyline.say(line.upper()), "make the string uppercase"), menu.quit_shell("quit", "quit the shell"), menu.repeat_shell("repeat", "repeat the question")], shell=True)
    >>> p.shell(m)
    perform stupid string tricks:
    1. reverse 
    2. upcase
    3. quit
    4. repeat
    5. help
    ? reverse this stuff
    ffuts siht
    ? upcase this other stuff
    THIS OTHER STUFF
    ? help rep
    = repeat
    
    repeat the question
    ? rep  
    perform stupid string tricks:
    1. reverse
    2. upcase
    3. quit
    4. repeat
    5. help
    ? q
    >>> 

Of course that is not how you would normally populate the menu object.

Lots of stuff is not demonstrated here, including non-blocking keyboard input, nifty autodetection of terminal dimensions, other kinds of questions/answers, different layouts for menus, lists, and questions, and such things.


    

