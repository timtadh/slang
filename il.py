#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

opsr = (
    'ADD', 'SUB', 'MUL', 'DIV', 'CALL', 'IPRM', 'OPRM', 'GPRM', 'RPRM',
    'EXIT', 'RTRN', 'CONT', 'IMM', 'PRNT',
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'BEQZ',
)
ops = dict((k, i) for i, k in enumerate(opsr))
sys.modules[__name__].__dict__.update(ops)

def run(il, funcs, params=None, var=None, stdout=None):
    if stdout == None: stdout = sys.stdout
    if not var: var = dict()
    nparams = list()
    rparams = list()
    for i in il:
        if i.op == IMM:
            var[i.result] = i.a
        elif i.op == DIV:
            var[i.result] = var[i.a] / var[i.b]
        elif i.op == MUL:
            var[i.result] = var[i.a] * var[i.b]
        elif i.op == SUB:
            var[i.result] = var[i.a] - var[i.b]
        elif i.op == ADD:
            var[i.result] = var[i.a] + var[i.b]
        elif i.op == EQ:
            var[i.result] = int(var[i.a] == var[i.b])
        elif i.op == NE:
            var[i.result] = int(var[i.a] != var[i.b])
        elif i.op == LT:
            var[i.result] = int(var[i.a] < var[i.b])
        elif i.op == LE:
            var[i.result] = int(var[i.a] <= var[i.b])
        elif i.op == GT:
            var[i.result] = int(var[i.a] > var[i.b])
        elif i.op == GE:
            var[i.result] = int(var[i.a] >= var[i.b])
        elif i.op == PRNT:
            print >>stdout, var[i.a]
        elif i.op == IPRM:
            if i.b[0] == 'f':
                nparams.insert(0, i.b)
            else:
                nparams.insert(0, var[i.b])
        elif i.op == OPRM:
            rparams.append(var[i.b])
        elif i.op == GPRM:
            var[i.result] = params[i.a]
        elif i.op == RPRM:
            var[i.result] = params[i.a]
        elif i.op == CALL:
            if i.a in funcs:
                params = run(funcs[i.a], funcs, nparams, var)
            else:
                params = run(funcs[var[i.a]], funcs, nparams, var)
            nparams = list()
        elif i.op == RTRN:
            return rparams
        elif i.op == BEQZ:
            if i.a == 0:
                Exception, "go to label %s" % (i.b)
        else:
            raise Exception, opsr[i.op]

class Inst(object):

    def __init__(self, op, a, b, result, label=None):
        self.op     = op
        self.a      = a
        self.b      = b
        self.result = result
        self.label  = label

    def __repr__(self): return str(self)

    def __str__(self):
        return '<%s %s %s -- %s>' % (opsr[self.op], str(self.a), str(self.b), str(self.result))


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


