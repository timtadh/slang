#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools
from analysis import first, follow, build_table
from gram_parser import EmptyString, EoS, Terminal

def parse(tokens, productions):
    def next():
        try:
            t = tokens.next()
            tok = Terminal(t.type)
            tok.value = t.value
            return tok
        except: return EoS()
    M = build_table(productions)

    stack = [ EoS(), productions[0] ]
    X = stack[-1]
    a = next()
    while X != EoS():
        #print X.sym, a.sym, stack
        if X == a:
            yield 0, a
            stack.pop()
            a = next()
        elif X.empty:
            yield 0, X
            stack.pop()
        elif X.terminal:
            raise Exception
        elif not M[(X, a)]:
            raise Exception
        elif M[(X, a)]:
            production = list(M[(X, a)][1])
            yield len(production), X
            stack.pop()
            for sym in (production[i] for i in range(len(production)-1, -1, -1)):
                stack.append(sym)
        X = stack[-1]

def default(X, *args):
    print X, args
    if hasattr(X, 'value'): return X.value
    return [arg for arg in args if arg is not None]

def processor(gen):
    def call(frame):
        return default(frame['me'].sym, *frame['args'])
    def collapse(stack):
        ret = None
        acc = list()
        while stack and stack[-1]['limit'] == len(stack[-1]['args']):
            acc.append(stack.pop())
        for frame in acc:
            ret = call(frame)
            if stack:
                stack[-1]['args'].append(ret)
        if stack and stack[-1]['limit'] == len(stack[-1]['args']):
            ret = collapse(stack)
        return ret
    stack = list()
    ret = None
    for children, sym in gen:
        if sym.terminal:
            stack[-1]['args'].append(sym.value)
        else:
            stack.append({'me':sym, 'args':list(), 'limit':children})
        ret = collapse(stack)
    return ret
