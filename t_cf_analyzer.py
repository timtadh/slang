#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import cStringIO

from sl_parser import Parser, Lexer
import cf_analyzer as cf
import il_gen
import nose

def analyze(s):
    out = cStringIO.StringIO()
    cf.analyze(*il_gen.generate(Parser().parse(s, lexer=Lexer())), stdout=out)
    return out.getvalue()


def t_expr_const():
    raise nose.SkipTest
    print analyze('print 2')

def t_recursive():
    #raise nose.SkipTest
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
