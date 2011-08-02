#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, subprocess

from frontend.sl_parser import Parser, Lexer
import cf, il, df
import abstract, example
import nose

def cf_analyze(s):
    entry, blocks, functions = il.il_gen.generate(Parser().parse(s, lexer=Lexer()), True)
    cf.analyze(entry, blocks, functions)
    return blocks, functions

@nose.tools.raises(TypeError)
def t_abstract_instantiate_fail():
    abstract.DataFlowAnalyzer()

def t_example_instantiate():
    example.ReachingDefintions()

def t_example_init():
    rd = example.ReachingDefintions()

    blocks, functions = cf_analyze('''
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
        ''')

    rd.init(functions['f2'])
    assert set(rd.defs.keys()) == set([('b3', 4), ('b2', 2), ('b5', 0), ('b4', 1), ('b4', 0), ('b3', 0), ('b3', 1), ('b2', 1), ('b2', 0)])
    assert set(t.id for t in rd.defs.values()) == set([1, 2, 4, 5, 6, 8, 9, 11])

def t_example_flowfunction():
    rd = example.ReachingDefintions()

    blocks, functions = cf_analyze('''
        f = func(x) {
            if (x > 0) {
                x = x + 5 - 3
                x = x - 4
                c = x*2
            }
            return c
        }
        print f(10)
        ''')

    rd.init(functions['f2'])
    print
    ff = rd.flow_function(blocks['b3'])

    assert ff(set([('b2', 0)])) == set([('b3', 4), ('b3', 5), ('b3', 2), ('b3', 0), ('b3', 1), ('b3', 6), ('b3', 7)])

def t_example_flowfunction_finally():
    rd = example.ReachingDefintions()

    blocks, functions = cf_analyze('''
        f = func(x) {
            c = 3
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            return c
        }
        print f(10)
        ''')

    rd.init(functions['f2'])
    ff_if = rd.flow_function(blocks['b2'])
    ff_then = rd.flow_function(blocks['b3'])
    ff_else = rd.flow_function(blocks['b5'])
    ff_finally = rd.flow_function(blocks['b4'])

    assert ff_if(set([('b4', 1)])) == set([('b4', 1), ('b2', 3), ('b2', 1), ('b2', 2), ('b2', 0)])
    assert ff_then(set([('b2', 1)])) == set([('b3', 4), ('b3', 0), ('b3', 1)])
    assert ff_else(set([('b2', 1)])) == set([('b5', 0)])
    assert ff_finally(set()) == set()

def t_example_ifthenelse_byhand():
    rd = example.ReachingDefintions()

    blocks, functions = cf_analyze('''
        f = func(x) {
            c = 3
            if (x > 0) {
                c = f(x-1)
            } else {
                c = x
            }
            return c
        }
        print f(10)
        ''')

    rd.init(functions['f2'])
    ff_if = rd.flow_function(blocks['b2'])
    ff_then = rd.flow_function(blocks['b3'])
    ff_else = rd.flow_function(blocks['b5'])
    ff_finally = rd.flow_function(blocks['b4'])

    _if = ff_if(set())
    _then = ff_then(_if)
    _else = ff_else(_if)
    _final = ff_finally(rd.join(_then, _else))

    assert set(d for d in _if if d in rd.types[2]) == set([('b2', 1)])
    assert set(d for d in _then if d in rd.types[2]) == set([('b3', 4)])
    assert set(d for d in _else if d in rd.types[2]) == set([('b5', 0)])
    assert set(d for d in _final if d in rd.types[2]) == set([('b3', 4), ('b5', 0)])
