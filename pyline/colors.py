class EffectBase(object):
    alleffects = {}
    def __getattribute__(self, attrname):
        if attrname == 'alleffects':
            return EffectBase.alleffects
        if attrname == 'followed_by':
            return object.__getattribute__(self, attrname)
        alleffects = EffectBase.alleffects
        if attrname in alleffects:
            return self.followed_by(alleffects[attrname])
        raise AttributeError
    def followed_by(self, nexteffect):
        return nexteffect

class EffectSequence(EffectBase):
    def __init__(self, *seq):
        EffectBase.__init__(self)
        self.effects = seq
    def __getattribute__(self, attrname):
        if attrname in ("effects", "followed_by", "__getitem__", "__str__",
                        "effectize"):
            return object.__getattribute__(self, attrname)
        return EffectBase.__getattribute__(self, attrname)
    def followed_by(self, nexteffect):
        return EffectSequence(*(self.effects+(nexteffect,)))
    def __getitem__(self, text):
        for e in reversed(self.effects):
            text = e.effectize(text)
        return clear.effectize(text)
    effectize = __getitem__
    __format__ = __getitem__
    def __str__(self):
        return ''.join(e.code for e in self.effects)

class Effect(EffectBase):
    def __init__(self, code, *names):
        EffectBase.__init__(self)
        for name in names:
            self.alleffects[name] = self
        self.code = code
    def __getattribute__(self, attrname):
        if attrname in ("code", "followed_by", "__getitem__", '__str__',
                        'effectize'):
            return object.__getattribute__(self, attrname)
        return EffectBase.__getattribute__(self, attrname)
    def followed_by(self, nexteffect):
        return EffectSequence(self, nexteffect)
    def __getitem__(self, text):
        return clear.effectize(self.code + text)
    __format__ = __getitem__
    def effectize(self, text):
        return self.code + text
    def __str__(self):
        return self.code

class NullEffect(EffectBase):
    def __getattribute__(self, _):
        return self
    def __format__(self, text):
        return text

class Replacer(Effect):
    def __init__(self, orig, repl, *names):
        self.orig = orig
        self.repl = repl
        Effect.__init__(self, '', *names)
    def __getattribute__(self, k):
        if k in ("orig", "repl"):
            return object.__getattribute__(self, k)
        return Effect.__getattribute__(self, k)
    def __getitem__(self, text):
        return text.replace(self.orig, self.repl)
    effectize = __getitem__
    __format__ = __getitem__
    def __str__(self):
        return ''

class PostEffect(Effect):
    def __getitem__(self, text):
        return text + self.code
    __format__ = __getitem__
    effectize = __getitem__

class ColorScheme(object):
    def __init__(self, **ks):
        self.colormap = {}
        for (k,v) in ks.iteritems():
            if isinstance(v, (str,unicode)):
                self.colormap[k] = v.split()
            else:
                self.colormap[k] = v
    def __getattribute__(self, attrname):
        if attrname == 'colormap':
            return object.__getattribute__(self, attrname)
        cm = self.colormap
        effects = cm.get(attrname, None)
        if not effects: return getattr(e, attrname)
        effect = e
        while effects:
            effect = getattr(effect, effects[0])
            effects = effects[1:]
        return effect
    
clear = PostEffect('\033[0m', 'clear', 'reset') 
Effect('\033[1m', 'bold')
Effect('\033[K', 'erase_line', 'el')
Effect('\033[P', 'erase_char', 'ec')
Effect('\033[2m', 'dark')
Effect('\033[4m', 'underscore', 'underline', 'under', 'ul')
Effect('\033[5m', 'blink')
Effect('\033[7m', 'reverse')
Effect('\033[8m', 'concealed')
Effect('\033[30m', 'black')
Effect('\033[31m', 'red')
Effect('\033[32m', 'green')
Effect('\033[33m', 'yellow')
Effect('\033[34m', 'blue')
Effect('\033[35m', 'magenta')
Effect('\033[36m', 'cyan')
Effect('\033[37m', 'white')
Effect('\033[40m', 'on_black')
Effect('\033[41m', 'on_red')
Effect('\033[42m', 'on_green')
Effect('\033[43m', 'on_yellow')
Effect('\033[44m', 'on_blue')
Effect('\033[45m', 'on_magenta')
Effect('\033[46m', 'on_cyan')
Effect('\033[47m', 'on_white')
Replacer('\0', ']', 'zb')
e = EffectBase()
none = NullEffect()
