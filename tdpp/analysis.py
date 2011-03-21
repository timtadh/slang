#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from gram_parser import parse, EmptyString, EoS,  NonTerminal

def first(productions, sym):
    if sym.terminal: return set([sym])
    symbols = set()
    for p in productions[sym]:
        all_e = True
        for psym in p:
           psym_first = first(productions, psym)
           symbols |= psym_first
           if EmptyString() not in psym_first:
               all_e = False
               break
        if all_e:
            symbols.add(EmptyString())
    return symbols

class follow(object):

    cache = dict()

    def __new__(cls, productions, sym):
        if sym in cls.cache: return cls.cache[sym]
        if sym.terminal: raise Exception, "Follow does not accept terminal symbols."
        symbols = set()
        if sym == productions[0]:
            symbols |= set([EoS()])
        for nt, p in productions.containing(sym):
            if sym not in p: raise Exception, "Symbol not in production"
            i = p.index(sym)
            if i+1 < len(p):
                f = first(productions, p[i+1])
                if EmptyString() in f:
                    f.remove(EmptyString())
                    symbols |= follow(productions, nt)
                symbols |= f
            elif i+1 == len(p) and sym != nt:
                symbols |= follow(productions, nt)
        cls.cache[sym] = symbols
        return symbols

