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
    #print
    #print

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
