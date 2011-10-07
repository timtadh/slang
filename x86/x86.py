#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

## Supported x86 Operators
opsr = (
    'movl', 'popl', 'pushl', 'leal',
    'addl', 'decl', 'incl',
    'subl', 'negl',
    'divl', 'idivl', 'mull', 'imull',
    'cmpl',
    'andl', 'notl', 'orl', 'xorl',
    'sall', 'sarl', 'shll', 'shrl',
    'int', 'call', 'ret', 'jmp',
    'je', 'jne', 'jl', 'jnl', 'jnle', 'jle',
        'jg', 'jng', 'jge', 'jnge',

    'push', 'leave', 'call',
    'nop',
)

## Supported x86 Registers
regsr = (
    'eax', 'ebx', 'ecx', 'edx', 'edi', 'esi',
    'ebp', 'esp', 'eip', 'eflags',
    'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'r8',
)

_ops = dict(("_"+op, i) for i, op in enumerate(opsr))
_regs = dict(("_"+reg, i) for i, reg in enumerate(regsr))
sys.modules[__name__].__dict__.update(_ops)
sys.modules[__name__].__dict__.update(_regs)

class label(object):
    '''Represents a label in the asm.'''

    def __init__(self, name):
        '''@param name : the name of the label.'''
        self.name = name

    def __str__(self):
        return '%s:' % (self.name)

class reg(object):
    '''Represents an x86 register. For a list of registers see regsr.'''

    def __init__(self, rnum):
        '''Create a reg object.
        @param rnum : The number representing the register. The registers are
                      defined in regsr. The rnum corresponds to the index in
                      regsr.
        '''
        self.rnum = rnum
    
    @property
    def reg(self):
        return regsr[self.rnum]

    def __str__(self):
        return ''.join(['%', regsr[self.rnum]])

class inst(object):
    '''Represents any x86 instruction.'''

    INDENT = 2

    def __init__(self, op, x=None, y=None):
        '''Create an instruction object representing the x86 instruction
        @param op : The integer (defined in "opsr" and "_ops")
        @param x  : The first arg. Can be anything that has a proper __str__
                    and represents the argument.
        @param y  : The second arg.

        op is required. If y exists then so must x.
        ie. (op is not None) and (y is not None --> x is not None)
        '''

        # assert  y is None --> x is None        logical implication
        # all logical implications can be rewritten
        #      X --> Y
        #      ~X or Y
        assert (op is not None) and ((y is None) or (x is not None))
        self.op = op
        self.x  = x
        self.y  = y

    def __str__(self):
        ## We want to pretty print these instructions such that the size of
        ## each field is fixed. So it can't just be ', '.join([op, x, y])

        ## Static Info
        indt = ' '*self.INDENT
        op   = opsr[self.op]
        args = [arg for arg in [self.x, self.y] if arg]

        ## We only want to append ',' if they are in the middle
        def string(s, i):
            if i == len(args) - 1: return str(s)
            else: return str(s) + ','

        ## Create the format string, with a insert location for each argument.
        line = (indt + '%-6s ' % op + ' '.join('%-10s' for arg in args))

        ## Format the string using a special toString for each arg which
        ## conditionally inserts the ','.
        line = line % tuple(string(arg, i) for i, arg in enumerate(args))

        return line

def __inst(op):
    '''A "decorator" for x86 operators so we can type x86.movl(...) instead of
    x86.inst(x86.movl, ...). Generates a function which instantiates the inst.
    '''
    def wrap(*args):
        try:
            return inst(op, *args)
        except Exception as e:
            e.args = [arg for arg in e.args] + [
                "Could not instantiate Inst for '%s' with %s" % (opsr[op], str(args))
            ]
            raise e
    wrap.func_name = 'op_%s' % op
    wrap.func_doc = 'generating function for x86 inst %s' % op
    return wrap


def cint(v):
    return '$0x%x' % v

def loc(typ):
    return '%i(%s)' % (typ.offset, typ.basereg)

def mem(reg, offset):
    return '%i(%s)' % (offset, reg)

def static(lbl, base='', index='', mul=None):
    if mul is None:
        return '%s(%s)' % (lbl, base)

    return '%s(%s, %s, %i)' % (lbl, base, index, mul)


ops = dict((op, __inst(i)) for i, op in enumerate(opsr))
regs = dict((r, reg(i)) for i, r in enumerate(regsr))
sys.modules[__name__].__dict__.update(ops)
sys.modules[__name__].__dict__.update(regs)
