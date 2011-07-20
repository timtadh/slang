#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, subprocess

from sl_parser import Parser, Lexer
import cf_analyzer as cf
import cf_struct as cfs
import il_gen, il
import nose

img_dir = os.path.abspath('./imgs')

def analyze(s):
    entry, blocks, functions = il_gen.generate(Parser().parse(s, lexer=Lexer()))
    cf.analyze(entry, blocks, functions)
    return functions

def mock():
    return cf.analyze.__mock__()

def dot(name, dotty):
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    fname = os.path.join(img_dir, name) + '.png'

    p = subprocess.Popen(['dot', '-Tpng', '-o', fname], stdin=subprocess.PIPE)
    p.stdin.write(dotty + '\0')
    p.stdin.close()
    p.wait()


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

    return [b1, b2, b3, b4], b1, 2, 0

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
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.CHAIN
    assert set(nset) == set(blks)

def t_acyclic_2xchain():
    i = I()
    blks, cblk, postmax, postctr = join(chain(i), chain(i))
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.CHAIN
    assert set(nset) == set(blks)

def t_acyclic_chain_ifthen():
    i = I()
    _chain = chain(i)
    _if_then = if_then(i)
    blks, cblk, postmax, postctr = join(_chain, _if_then)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.CHAIN
    assert set(nset) == set(_chain[0] + [ _if_then[0][0] ])

def t_acyclic_chain_ifthenelse():
    i = I()
    _chain = chain(i)
    _if_then_else = if_then_else(i)
    blks, cblk, postmax, postctr = join(_chain, _if_then_else)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.CHAIN
    assert set(nset) == set(_chain[0] + [ _if_then_else[0][0] ])

def t_acyclic_ifthen():
    i = I()
    blks, cblk, postmax, postctr = if_then(i)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN
    assert set(nset) == set(blks)

def t_acyclic_ifthenelse():
    i = I()
    blks, cblk, postmax, postctr = if_then_else(i)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN_ELSE
    assert set(nset) == set(blks)

def t_acyclic_ifthen_chain():
    i = I()
    _if_then = if_then(i)
    _chain = chain(i)
    blks, cblk, postmax, postctr = join(_if_then, _chain)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN
    assert set(nset) == set(_if_then[0])

def t_acyclic_ifthenelse_chain():
    i = I()
    _if_then_else = if_then_else(i)
    _chain = chain(i)
    blks, cblk, postmax, postctr = join(_if_then_else, _chain)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN_ELSE
    assert set(nset) == set(_if_then_else[0])

def t_expr_const():
    raise nose.SkipTest
    print analyze('print 2')

def t_ite():
    #raise nose.SkipTest
    dotty = analyze('''
        f = func(x) {
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            return c
        }
        print f(10)
        ''')['f2'].tree.dotty()
    dot('cf.ite', dotty)

def t_ite_it():
    #raise nose.SkipTest
    dotty = analyze('''
        f = func(x) {
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            if (x == 0) {
                print x
            }
            return c
        }
        print f(10)
        ''')['f2'].tree.dotty()
    dot('cf.ite_it', dotty)
    #assert False


def t_nest_ite():
    #raise nose.SkipTest
    dotty = analyze('''
        f = func(x) {
            if (x > 0) {
                if (x/2 + x/2 == x) { // then it is even
                    c = f(x+1)
                } else {
                    c = f(x-3)
                }
            } else {
                if (x < 5) {
                    if (x != 0) {
                        x = x - 1
                    }
                    c = x
                } else {
                    c = 10
                }
            }
            return c
        }
        print f(10)
        ''')['f2'].tree.dotty()
    dot('cf.ite_it', dotty)
