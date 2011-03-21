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

def t_parse_simple_gram():
    from tdpp.t_analysis import productions, Lexer
    from tdpp.parser import parse
    from ast import Node
    lexer = Lexer()
    lexer.input('6+7*4+3*2*(4+3)')
    stack = list()
    root = None
    for children, sym in parse((t for t in lexer), productions):
        if not sym.value: node = Node(sym.sym)
        else: node = Node(sym.value)
        if not root: root = node

        if stack:
            stack[-1]['node'].addkid(node)
            stack[-1]['children'] -= 1
            if stack[-1]['children'] <= 0:
                stack.pop()
        if children:
            stack.append({'node':node, 'children':children})
    print root.dotty()

if __name__ == '__main__':
    t_parse_simple_gram()
