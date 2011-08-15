#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

def inst(indent, op, *args):
    line = (' '*indent + '%-5s' % op + ', '.join('%7s' for arg in args))
    line = line % tuple(str(arg) for arg in args)
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


))
sys.modules[__name__].__dict__.update(ops)


sys.modules[__name__].__dict__.update(dict((reg, '%'+reg) for reg in (
    'eax', 'ebx', 'ecx', 'edx', 'edi', 'esi',
    'ebp', 'esp', 'eip', 'eflags',
)))

