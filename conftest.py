# just having this file in this directory allows us to import pyline
# in the files in the test/ directory. We don't actually do any setup here!
import cStringIO

def sio(txt=''):
    if txt:
        inp = cStringIO.StringIO()
        set_inp(inp, txt)
        return inp
    return cStringIO.StringIO()
def reset(sio):
    sio.seek(0)
    sio.truncate()
def set_inp(sio, txt):
    reset(sio)
    sio.write(txt)
    sio.seek(0)

def no_clear(txt):
    return txt.replace('\x1b[0m', '')
