#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import cStringIO

from sl_parser import Parser, Lexer
import cf_analyzer as cf
import cf_struct as cfs
import il_gen, il
import nose

def analyze(s):
    out = cStringIO.StringIO()
    cf.analyze(*il_gen.generate(Parser().parse(s, lexer=Lexer())), stdout=out)
    return out.getvalue()

def mock():
    return cf.analyze.__mock__()

def I():
    def gen():
        x = 0
        while True:
            x += 1
            yield x
    g = gen()
    def i():
        return g.next()
    return i

def chain(i):
    b1 = il.Block('b%i' % i())
    b2 = il.Block('b%i' % i())
    b3 = il.Block('b%i' % i())
    b4 = il.Block('b%i' % i())
    b5 = il.Block('b%i' % i())

    b1.next += [ b2 ]
    b2.next += [ b3 ]
    b3.next += [ b4 ]
    b4.next += [ b5 ]

    b2.prev += [ b1 ]
    b3.prev += [ b2 ]
    b4.prev += [ b3 ]
    b5.prev += [ b4 ]

    return [b1, b2, b3, b4, b5], b3, 4, 2

def if_then(i):
    b1 = il.Block('b%i' % i())
    b2 = il.Block('b%i' % i())
    b3 = il.Block('b%i' % i())

    b1.next += [ b2, b3 ]
    b2.next += [ b3 ]

    b2.prev += [ b1 ]
    b3.prev += [ b2, b3 ]

    return [b1, b2, b3], b1, 2, 0

def if_then_else(i):
    b1 = il.Block('b%i' % i())
    b2 = il.Block('b%i' % i())
    b3 = il.Block('b%i' % i())
    b4 = il.Block('b%i' % i())

    b1.next += [ b2, b3 ]
    b2.next += [ b4 ]
    b3.next += [ b4 ]

    b2.prev += [ b1 ]
    b3.prev += [ b1 ]
    b4.prev += [ b2, b3 ]

    return [b1, b2, b3], b1, 2, 0

def join(*grps):
    blks = list()
    cblk = None
    postmax = 0
    postctr = 0

    w, x, y, z = grps[0]
    blks += w
    cblk = x
    postmax = y
    postctr = z

    for f in grps[1:]:
        w,x,y,z = f
        e = blks[-1]
        s = w[0]
        e.next += [ s ]
        s.prev += [ e ]
        blks += w
        postmax += (y+1)

    return blks, cblk, postmax, postctr

def t_acyclic_chain():
    i = I()
    blks, cblk, postmax, postctr = chain(i)
    rtype, nset = mock().acyclic(blks, cblk)
    assert rtype == cfs.CHAIN
    assert nset == set(blks)

def t_acyclic_chain():
    i = I()
    blks, cblk, postmax, postctr = join(chain(i), chain(i))
    rtype, nset = mock().acyclic(blks, cblk)
    assert rtype == cfs.CHAIN
    assert nset == set(blks)

def t_acyclic_chain_ifthen():
    i = I()
    _chain = chain(i)
    _if_then = if_then(i)
    blks, cblk, postmax, postctr = join(_chain, _if_then)
    rtype, nset = mock().acyclic(blks, cblk)
    assert rtype == cfs.CHAIN
    assert nset == set(_chain[0] + [ _if_then[0][0] ])

def t_acyclic_chain_ifthenelse():
    i = I()
    _chain = chain(i)
    _if_then_else = if_then_else(i)
    blks, cblk, postmax, postctr = join(_chain, _if_then_else)
    rtype, nset = mock().acyclic(blks, cblk)
    assert rtype == cfs.CHAIN
    assert nset == set(_chain[0] + [ _if_then_else[0][0] ])

def t_expr_const():
    raise nose.SkipTest
    print analyze('print 2')

def t_recursive():
    raise nose.SkipTest
    print analyze('''
        f = func(x) {
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            return c
        }
        print f(10)
        ''')
    assert False
