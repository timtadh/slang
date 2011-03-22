#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools, itertools
from gram_parser import parse, EmptyString, EoS,  NonTerminal, Terminal

def first(productions, sym):
    if isinstance(sym, tuple):
        symbols = set()
        for s in sym:
            first_s = first(productions, s)
            symbols |= first_s
            if EmptyString() not in first_s:
                break
        return symbols
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


def LL1(productions, DEBUG=False):
    ret = True
    for nt, nt_productions in productions.iteritems():
        follow_nt = follow(productions, nt)
        for a,b in itertools.product(nt_productions, nt_productions):
            if a == b: continue
            first_a = first(productions, a)
            first_b = first(productions, b)

            if (first_a & first_b) != set():
                if DEBUG:
                    print
                    print 'Error 1 @%s' % nt.sym
                    print ' '*4, a
                    print ' '*8, first_a
                    print ' '*4, b
                    print ' '*8, first_b
                ret = False
            if (EmptyString() in first_a) and ((first_a & follow_nt) != set()):
                if DEBUG:
                    print
                    print 'Error 2 @%s' % nt.sym
                    print ' '*4, a
                    print ' '*4, b
                ret = False
            if (EmptyString() in first_b) and ((first_b & follow_nt) != set()):
                if DEBUG:
                    print
                    print 'Error 3 @%s' % nt.sym
                    print ' '*4, a
                    print ' '*4, b
                ret = False
    return ret

def build_table(productions, DEBUG=False):
    M = dict()
    def s(key, value):
        if M[key] is not None:
            raise Exception
        M[key] = value

    assert LL1(productions)
    FIRST = functools.partial(first, productions)
    FOLLOW = functools.partial(follow, productions)

    tokens = [Terminal(t) for t in productions.tokens] + [EmptyString(), EoS()]

    for nt in productions.keys():
        for t in tokens:
            M[(nt, t)] = None
        #M[(nt, EoS())] = set()

    for nt, nt_productions in productions.iteritems():
        follow_nt = FOLLOW(nt)
        for i, p in enumerate(nt_productions):
            first_p = FIRST(p)
            for sym in first_p:
                if sym.terminal and not sym.empty and not sym.eos:
                    s((nt, sym), (nt, i))
            if EmptyString() in first_p:
                for sym in follow_nt:
                    s((nt, sym), (nt, i))
            if EmptyString() in first_p and EoS in follow_nt:
                s((nt, EoS()), (nt, i))
    if DEBUG:
        print
        for nt in productions.keys():
            for t in tokens:
                if M[(nt, t)] is None:
                    print '<%s, %s>' % (nt.sym, t.sym)
                else:
                    p = M[(nt, t)]
                    print (
                        '%-25s %s' % (
                            '<%s, %s>' % (nt.sym, t.sym),
                            '%s : %s' % (p[0].sym, ' '.join(str(x.sym) for x in productions[p[0]][p[1]]))
                        )
                    )
            print
                    #(nt.sym, t.sym), p[0].sym, ':=', ' '.join(str(x.sym) for x in p[1])
    return M
