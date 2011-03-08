#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

opsr = (
    'ADD', 'SUB', 'MUL', 'DIV', 'CALL', 'IPRM', 'OPRM', 'GPRM', 'RPRM',
    'EXIT', 'RTRN', 'CONT', 'IMM', 'PRNT',
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'BEQZ', 'NOP', 'J'
)
ops = dict((k, i) for i, k in enumerate(opsr))
sys.modules[__name__].__dict__.update(ops)

def run(il, labels, params=None, var=None, stdout=None):
    if stdout == None: stdout = sys.stdout
    if not var: var = dict()
    nparams = list()
    rparams = list()
    print params
    c = 0
    while c < len(il):
        i = il[c]
        if i.op == IMM:
            var[i.result.name] = i.a
        elif i.op == DIV:
            var[i.result.name] = var[i.a.name] / var[i.b.name]
        elif i.op == MUL:
            var[i.result.name] = var[i.a.name] * var[i.b.name]
        elif i.op == SUB:
            var[i.result.name] = var[i.a.name] - var[i.b.name]
        elif i.op == ADD:
            var[i.result.name] = var[i.a.name] + var[i.b.name]
        elif i.op == EQ:
            var[i.result.name] = 1 - int(var[i.a.name] == var[i.b.name])
        elif i.op == NE:
            var[i.result.name] = 1 - int(var[i.a.name] != var[i.b.name])
        elif i.op == LT:
            var[i.result.name] = 1 - int(var[i.a.name] < var[i.b.name])
        elif i.op == LE:
            var[i.result.name] = 1 - int(var[i.a.name] <= var[i.b.name])
        elif i.op == GT:
            var[i.result.name] = 1 - int(var[i.a.name] > var[i.b.name])
        elif i.op == GE:
            var[i.result.name] = 1 - int(var[i.a.name] >= var[i.b.name])
        elif i.op == PRNT:
            print >>stdout, var[i.a.name]
        elif i.op == IPRM:
            if isinstance(i.b.type, Func):
                nparams.insert(0, i.b)
            else:
                nparams.insert(0, var[i.b.name])
        elif i.op == OPRM:
            rparams.append(var[i.b.name])
        elif i.op == GPRM:
            var[i.result.name] = params[i.a]
            print i.result, var[i.result.name]
        elif i.op == RPRM:
            var[i.result.name] = params[i.a.name]
        elif i.op == CALL:
            print i.a
            if isinstance(i.a.type, Func):
                params = run(i.a.type.code, i.a.type.labels, nparams, var)
            else:
                params = run(var[i.a.name].type.code, var[i.a.name].type.labels, nparams, var)
            nparams = list()
        elif i.op == RTRN:
            return rparams
        elif i.op == BEQZ:
            print i.a
            if var[i.a.name] == 0:
                #raise Exception, "go to label %s" % (i.b)
                c = labels[i.b]
                continue;
        elif i.op == J:
            c = labels[i.a]
            continue;
        elif i.op == NOP:
            pass
        else:
            raise Exception, opsr[i.op]
        c += 1

class Inst(object):

    def __init__(self, op, a, b, result, label=None):
        self.op     = op
        self.a      = a
        self.b      = b
        self.result = result
        self.label  = label

    def __repr__(self): return str(self)

    def __str__(self):
        if self.label is None:
            return '<%s %s %s -- %s>' % (opsr[self.op], str(self.a), str(self.b), str(self.result))
        s = '<%s %s %s -- %s>' % (opsr[self.op], str(self.a), str(self.b), str(self.result))
        s = '%-25s : %s' % (s, self.label)
        return s

class Type(object):

    def cast(self, cls):
        raise TypeError, "invalid cast"

class Int(object):

    def __init__(self, basereg=None, offset=None):
        self.basereg = basereg
        self.offset = offset

    def cast(self, cls):
        if cls is FuncPointer:
            return FuncPointer(self.basereg, self.offset)
        return super(Int, self).cast(cls)

    def __repr__(self):
        if self.basereg is None:
            return '{Int}'
        return '{Int %s %s}' % (self.basereg, self.offset)

class Func(object):

    def __init__(self, code):
        self._code = code
        self._labels = None

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, val):
        self._code = val

    @property
    def labels(self):
        #print self._labels
        assert self._labels is not None
        return self._labels

    @labels.setter
    def labels(self, val):
        #print self._labels, val
        self._labels = val

    def __repr__(self):
        if self.code is None:
            return '{Func}'
        return '{Func %d}' % (len(self.code))

class FuncPointer(Int):
    def __repr__(self):
        if self.basereg is None:
            return '{FuncPointer}'
        return '{FuncPointer %s %s}' % (self.basereg, self.offset)
