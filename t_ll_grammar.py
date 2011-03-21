#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sl_parser
from tdpp.analysis import LL1, build_table
from tdpp.gram_parser import parse


f = open('ll_grammar.txt', 'r')
grammar = f.read()
f.close()
productions = parse(sl_parser.tokens, grammar)

def t_llgrammar():

    assert LL1(productions)

def t_build():
    build_table(productions, True)
