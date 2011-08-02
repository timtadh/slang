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
    entry, blocks, functions = il.il_gen.generate(Parser().parse(s, lexer=Lexer()))
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
    assert False
