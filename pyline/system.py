import sys

def get_character(inp=sys.stdin):
    if not inp.isatty():
        return inp.read(1)
    return _get_character(inp)

if sys.platform == 'win32':
    pass
elif sys.platform in ('riscos', 'os2', 'os2emx', 'atheos'):
    pass
else:
    import termios
    try:
        import curses
        def _get_character(inp=sys.stdin):
            old = termios.tcgetattr(inp)
            new = old[:]
            new[-1] = old[-1][:]
            new[3] &= ~(termios.ECHO | termios.ICANON)
            new[-1][termios.VMIN] = 1
            try:
                termios.tcsetattr(inp, termios.TCSANOW, new)
                return inp.read(1)
            finally:
                termios.tcsetattr(inp, termios.TCSANOW, old)

        def terminal_size():
            try:
                win = curses.initscr()
                return reversed(win.getmaxyx())
            finally:
                curses.endwin()
            return (80, 40)
    except ImportError:
        import re
        from subprocess import Popen, PIPE
        output = lambda a: Popen(a, stdout=PIPE).communicate()[0].rstrip()
        try:
            output(["stty"])
        except OSError, e:
            if e.errno != 2: raise
            sys.stderr.write("To use PyLine, you need either the curses module or the stty program.\n")

        def _get_character(inp=sys.stdin):
            state = output(["stty","-g"])
            try:
                output("stty raw -echo -icanon isig".split())
                return inp.read(1)
            finally:
                output(["stty",state])

        def terminal_size():
            return tuple(map(int, output(["stty", "size"]).split()))
