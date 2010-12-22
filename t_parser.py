#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import nose.tools
from sl_parser import Parser, Lexer

#def t_simple():
    #parse = Parser().parse
    #assert parse('''
        #f = func(a, b) {
            #c = add(a,b)
            #return c, b
        #}
        #r, r2 = f(2,3)
        #print(r)
        #exit()
    #''', lexer=Lexer())
    #nose.tools.assert_raises(Exception, parse, '''
        #f,b = func(a, b) {
            #c = add(a,b)
            #return c, b
        #}
        #r, r2 = f(2,3)
        #print(r)
        #exit()
    #''', lexer=Lexer()
    #)
