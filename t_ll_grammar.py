#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sl_parser
from tdpp.analysis import LL1
from tdpp.gram_parser import parse


def t_llgrammar():
    f = open('ll_grammar.txt', 'r')
    grammar = f.read()
    f.close()

    productions = parse(sl_parser.tokens, grammar)
    assert LL1(productions)
