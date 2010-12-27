#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

opsr = (
    'ADD', 'SUB', 'MUL', 'DIV', 'MV', 'CALL', 'IPRM', 'OPRM', 'EXIT', 'RTRN',
    'CONT'
)
ops = dict((k, i) for i, k in enumerate(opsr))
sys.modules[__name__].__dict__.update(ops)

class Inst(object):

    def __init__(self, op, a, b, result):
        self.op     = op
        self.a      = a
        self.b      = b
        self.result = result

class Func(object):

    def __init__(self, inn, out, label=None):
        self.label = label
        self.inn = inn
        self.out = out

    def __eq__(self, b):
        if not isinstance(b, Func):
            return False
        if len(self.inn) != len(b.inn) or len(self.out) != len(b.out):
            return False
        for i,A in enumerate(self.inn):
            B = b.inn[i]
            if A != B:
                return False
        for i,A in enumerate(self.out):
            B = b.out[i]
            if A != B:
                return False
        return True

    def __ne__(self, b):
        return not self.__eq__(b)

    def __repr__(self): return str(self)

    def __str__(self):
        s = '<il.Func "%s" in:%s out:%s>' % (self.label, self.inn, self.out)
        return s

class Int(object):

    def __eq__(self, b): return isinstance(b, Int)
    def __ne__(self, b): return not isinstance(b, Int)
    def __repr__(self): return str(self)

    def __str__(self):
        s = '<il.Int>'
        return s

class Const(object):

    def __init__(self, value):
        self.value = value

    def __eq__(self, b): return isinstance(b, Const)
    def __ne__(self, b): return not isinstance(b, Const)

def coerce(a, b):
    '''Returns type to coerce a to b based on type rules.'''
    if isinstance(b, Func) and a == b:
        return Func
    elif isinstance(b, Int) and (a == b or isinstance(a, Const)):
            return Int
    else:
        raise (
            TypeError(
                "Type '%s' is unsupported as a the coerce to param" % (str(b))
            )
        )
