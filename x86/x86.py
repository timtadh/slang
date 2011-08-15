#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

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


def inst(indent, op, *args):
    return ' '*indent + '%-5s' % str(op), ' '.join(arg for arg in args)

def __inst(op):
    def wrap(indent, *args):
        return inst(indent, op, *args)
    wrap.func_name = 'op'
    wrap.func_doc = 'generating function for x86 inst %s' % op
    return wrap

def label(name):
    return '%s:' % (name)
