#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import cStringIO

from sl_parser import Parser, Lexer
from table import SymbolTable
import il_gen, il

def run(s):
    out = cStringIO.StringIO()
    il.run(*il_gen.generate(Parser().parse(s, lexer=Lexer())), stdout=out)
    return out.getvalue()

def t_expr_const():
    assert '2' == run('print 2').rstrip('\n')

def t_expr_ops():
    assert '6' == run('print 2*3').rstrip('\n')
    assert '6' == run('print 1+2+3').rstrip('\n')
    assert '6' == run('print 9-3').rstrip('\n')
    assert '6' == run('print 12/2').rstrip('\n')

def t_expr_compound():
    assert '6' == run('print 4*3/2').rstrip('\n')
    assert '6' == run('print (3+9)*4/8').rstrip('\n')
    print run('print ((9-3)+(5-3))/2 + 2').rstrip('\n')
    assert '6' == run('print 12/2').rstrip('\n')

