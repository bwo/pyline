"""Methods for laying out out items into a list.
"""

from utils import real_len

def inline_simple(items, firstsep=None, finalsep=None):
    firstsep = firstsep or ', '
    finalsep = finalsep or ' or '
    totitems = len(items)
    if totitems == 1:
        return items[0]
    elif totitems == 2:
        return finalsep.join(items)
    else:
        return finalsep.join((firstsep.join(items[:-1])+firstsep.strip(), items[-1]))

def inline(pyl_unused, items, *args):
    """Format the items in a way suitable for inline display. Two (optional) positional arguments are accepted. The first is inserted between all but the last two items, and the second is inserted between the last two; they default to ", " and " or ", respectively.

    ``inline(p, "a b c d e f g".split())`` -> ``"a, b, c, d, e, f, or g"``

    Note that the Oxford comma is employed!
"""
    if not args:
        firstsep = finalsep = None
    elif len(args) == 1:
        firstsep = args[0]
        finalsep = None
    else:
        firstsep, finalsep = args[:2]
    return inline_simple(items, firstsep, finalsep)

def rows(pyl, items, *junk):
    return '\n'.join(items)

def _columns_general(pyl, items, cols):
    longest = len(max(items, key=real_len))
    if not cols:
        cols = (pyl.wrap_at + 2) / (longest + 2)
    items = ["{1:<{0}}".format(longest+(len(i)-real_len(i)), i) for i in items]
    count = len(items)
    rows = count / cols + int(count % cols != 0)
    return items, rows, cols

def columns_down(pyl, items, *args):
    cols = args[0] if args else None
    items, rows, cols = _columns_general(pyl, items, cols)
    out = []
    for i in range(rows):
        out.append(items[i::rows])
    return '\n'.join('  '.join(line) for line in out)

def columns_across(pyl, items, *args):
    cols = args[0] if args else None
    items, rows, cols = _columns_general(pyl, items, cols)
    out = []
    while items:
        out.append(items[:cols])
        items = items[cols:]
    return '\n'.join('  '.join(line) for line in out)
