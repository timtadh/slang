#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

def inst(indent, op, *args):
    def string(s, i):
        if i == len(args) - 1: return str(s)
        else: return str(s) + ','
    line = (' '*indent + '%-6s ' % op + ' '.join('%-10s' for arg in args))
    line = line % tuple(string(arg, i) for i, arg in enumerate(args))
    return line

def __inst(op):
    def wrap(*args):
        return inst(2, op, *args)
    wrap.func_name = 'op'
    wrap.func_doc = 'generating function for x86 inst %s' % op
    return wrap

def label(name):
    return '%s:' % (name)

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


ops = dict((op, __inst(op)) for op in (
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


))
sys.modules[__name__].__dict__.update(ops)


sys.modules[__name__].__dict__.update(dict((reg, '%'+reg) for reg in (
    'eax', 'ebx', 'ecx', 'edx', 'edi', 'esi',
    'ebp', 'esp', 'eip', 'eflags',

    'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'r8',
)))

