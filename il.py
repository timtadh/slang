#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

opsr = (
    'ADD', 'SUB', 'MUL', 'DIV', 'MV', 'CALL', 'IPRM', 'OPRM', 'EXIT', 'RTRN', 'CONT'
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

    def __repr__(self): return str(self)

    def __str__(self):
        s = '<il.Func "%s" in:%s out:%s>' % (self.label, self.inn, self.out)
        return s

class Int(object):

    def __repr__(self): return str(self)

    def __str__(self):
        s = '<il.Int>'
        return s

class Const(object):

    def __init__(self, value):
        self.value = value
