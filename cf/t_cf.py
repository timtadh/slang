#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, subprocess, traceback

from frontend.sl_parser import Parser, Lexer
import cf
import struct as cfs
import il
from il import il_gen
import nose

GEN_IMGS = True
img_dir = os.path.abspath('./imgs')

def analyze(s):
    name = traceback.extract_stack()[-2][2]
    ast = Parser().parse(s, lexer=Lexer())
    table, blocks, functions = il_gen.generate(ast, debug=True)
    dot('ast.%s'%name, ast.dotty(), str(ast))
    dot('blks.%s'%name, functions['f2'].entry.dotty())
    cf.analyze(table, blocks, functions, debug=True)
    dot('cf.%s'%name, functions['f2'].tree.dotty())
    return functions

def mock():
    return cf.analyze.__mock__()

def dot(name, dotty, AST=None):
    if not GEN_IMGS: return
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    if AST:
        ast = os.path.join(img_dir, name) + '.ast'
        f = open(ast, 'w')
        f.write(AST)
        f.close()

    dot = os.path.join(img_dir, name) + '.dot'
    plain = os.path.join(img_dir, name) + '.plain'
    png = os.path.join(img_dir, name) + '.png'

    f = open(dot, 'w')
    f.write(dotty)
    f.close()

    p = subprocess.Popen(['dot', '-Tplain', '-o', plain], stdin=subprocess.PIPE)
    p.stdin.write(dotty + '\0')
    p.stdin.close()
    p.wait()

    p = subprocess.Popen(['dot', '-Tpng', '-o', png], stdin=subprocess.PIPE)
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

    b1.link(b2, il.UNCONDITIONAL)
    b2.link(b3, il.UNCONDITIONAL)
    b3.link(b4, il.UNCONDITIONAL)
    b4.link(b5, il.UNCONDITIONAL)

    return [b1, b2, b3, b4, b5], b3, 4, 2

def if_then(i):
    b1 = il.Block('b%i' % i())
    b2 = il.Block('b%i' % i())
    b3 = il.Block('b%i' % i())

    b1.link(b2, il.TRUE)
    b1.link(b3, il.FALSE)
    b2.link(b3, il.UNCONDITIONAL)

    return [b1, b2, b3], b1, 2, 0

def if_then_else(i):
    b1 = il.Block('b%i' % i())
    b2 = il.Block('b%i' % i())
    b3 = il.Block('b%i' % i())
    b4 = il.Block('b%i' % i())

    b1.link(b2, il.TRUE)
    b1.link(b3, il.FALSE)
    b2.link(b4, il.UNCONDITIONAL)
    b3.link(b4, il.UNCONDITIONAL)

    return [b1, b2, b3, b4], b1, 2, 0

def if_and_then_else(i):
    b1 = il.Block('b%i' % i())
    b2 = il.Block('b%i' % i())
    b3 = il.Block('b%i' % i())
    b4 = il.Block('b%i' % i())
    b5 = il.Block('b%i' % i())

    b1.link(b2, il.TRUE)
    b1.link(b3, il.FALSE)
    b2.link(b4, il.TRUE)
    b2.link(b3, il.FALSE)
    b3.link(b5, il.UNCONDITIONAL)
    b4.link(b5, il.UNCONDITIONAL)

    return [b1, b2, b3, b4, b5], b1, 4, 0

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
        e.link(s, il.UNCONDITIONAL)
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
    #raise nose.SkipTest
    i = I()
    blks, cblk, postmax, postctr = if_then(i)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    print ok, rtype
    print nset
    assert ok == True
    assert rtype == cfs.IF_THEN
    assert set(nset) == set(blks[:2])

def t_acyclic_ifthenelse():
    #raise nose.SkipTest
    i = I()
    blks, cblk, postmax, postctr = if_then_else(i)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN_ELSE
    assert set(nset) == set(blks[:3])

def t_acyclic_ifthen_chain():
    #raise nose.SkipTest
    i = I()
    _if_then = if_then(i)
    _chain = chain(i)
    blks, cblk, postmax, postctr = join(_if_then, _chain)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN
    assert set(nset) == set(_if_then[0][:2])

def t_acyclic_ifthenelse_chain():
    #raise nose.SkipTest
    i = I()
    _if_then_else = if_then_else(i)
    _chain = chain(i)
    blks, cblk, postmax, postctr = join(_if_then_else, _chain)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    assert ok == True
    assert rtype == cfs.IF_THEN_ELSE
    assert set(nset) == set(_if_then_else[0][:3])

def t_acyclic_ifandthenelse():
    #raise nose.SkipTest
    i = I()
    blks, cblk, postmax, postctr = if_and_then_else(i)
    ok, rtype, nset = mock().acyclic(blks, cblk)
    print cblk, cblk.next
    assert ok == True
    assert rtype == cfs.PROPER
    print nset, blks
    assert set(nset) == set(blks[:4])

def t_none():
    #raise nose.SkipTest
    tree = analyze('''
        var f = func(x) {
            return x
        }
        print f(10)
        ''')['f2'].tree
    #dot('cf.none', tree.dotty())
    assert not hasattr(tree, 'region_type')

def t_it():
    #raise nose.SkipTest
    f2 = analyze('''
        var f = func(x) {
            if (x > 0) {
                x = f(x-1)
            }
            return x
        }
        print f(10)
        ''')['f2']
    tree = f2.tree
    entry = f2.entry
    assert tree.region_type == cfs.CHAIN
    assert tree.children[0].region_type == cfs.IF_THEN

def t_ite():
    #raise nose.SkipTest
    f = analyze('''
        var f = func(x) {
            var c
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            return c
        }
        print f(10)
        ''')['f2']
    tree = f.tree
    assert tree.region_type == cfs.CHAIN
    assert tree.children[0].region_type == cfs.IF_THEN_ELSE


def t_ite_it():
    #raise nose.SkipTest
    f = analyze('''
        var f = func(x) {
            var c
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
        ''')['f2']
    tree = f.tree
    assert tree.region_type == cfs.CHAIN
    assert tree.children[0].region_type == cfs.IF_THEN_ELSE
    assert tree.children[1].region_type == cfs.CHAIN
    assert tree.children[1].children[0].region_type == cfs.IF_THEN


def t_nest_ite():
    #raise nose.SkipTest
    f = analyze('''
        var f = func(x) {
            var c
            if (x > 0) {
                if (x/2 + x/2 == x) { // then it is even
                    c = f(x+1)
                } else {
                    c = f(x-3)
                }
            } else {
                c = 10
                if (x < 5) {
                    if (x != 0) {
                        x = x - 1
                    }
                    c = x
                }
            }
            return c
        }
        print f(10)
        ''')['f2']
    tree = f.tree
    assert tree.region_type == cfs.CHAIN
    assert tree.children[0].region_type == cfs.IF_THEN_ELSE
    assert tree.children[0].children[1].region_type == cfs.CHAIN
    assert tree.children[0].children[2].region_type == cfs.CHAIN
    assert tree.children[0].children[1].children[0].region_type == cfs.IF_THEN_ELSE
    assert tree.children[0].children[2].children[0].region_type == cfs.IF_THEN
    assert tree.children[0].children[2].children[0].children[1].region_type == cfs.CHAIN
    assert tree.children[0].children[2].children[0].children[1].children[0].region_type == cfs.IF_THEN

def t_nest_ite_org():
    #raise nose.SkipTest
    f = analyze('''
        var f = func(x) {
            var c
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
        ''')['f2']
    tree = f.tree
    assert tree.region_type == cfs.CHAIN
    assert tree.children[0].region_type == cfs.IF_THEN_ELSE
    assert tree.children[0].children[1].region_type == cfs.CHAIN
    assert tree.children[0].children[2].region_type == cfs.CHAIN
    assert tree.children[0].children[1].children[0].region_type == cfs.IF_THEN_ELSE
    assert tree.children[0].children[2].children[0].region_type == cfs.IF_THEN_ELSE
    assert tree.children[0].children[2].children[0].children[1].region_type == cfs.CHAIN
    assert tree.children[0].children[2].children[0].children[1].children[0].region_type == cfs.IF_THEN

