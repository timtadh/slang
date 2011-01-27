#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from ply import yacc
from sl_lexer import tokens, Lexer
from ast import Node

## If you are confused about the syntax in this file I recommend reading the
## documentation on the PLY website to see how this compiler compiler's syntax
## works.
class Parser(object):

    tokens = tokens
    precedence = (    )

    def __new__(cls, **kwargs):
        ## Does magic to allow PLY to do its thing.
        self = super(Parser, cls).__new__(cls, **kwargs)
        self.table = dict()
        self.loc = list()
        self.yacc = yacc.yacc(module=self, **kwargs)
        return self.yacc

    def get_table(self):
        c = self.table
        for s in self.loc:
            c = self.table[c]
        return c

    def p_Start(self, t):
        'Start : Arith'
        t[0] = t[1]

    def p_Arith(self, t):
        'Arith : Div'
        t[0] = Node('Arith').addkid(t[1])

    def p_Div1(self, t):
        'Div : Div SLASH Mul'
        t[0] = Node('/').addkid(t[1]).addkid(t[3])

    def p_Div2(self, t):
        'Div : Mul'
        t[0] = t[1]

    def p_Mul1(self, t):
        'Mul : Mul STAR Sub'
        t[0] = Node('*').addkid(t[1]).addkid(t[3])

    def p_Mul2(self, t):
        'Mul : Sub'
        t[0] = t[1]

    def p_Sub1(self, t):
        'Sub : Sub DASH Add'
        t[0] = Node('-').addkid(t[1]).addkid(t[3])

    def p_Sub2(self, t):
        'Sub : Add'
        t[0] = t[1]

    def p_Add1(self, t):
        'Add : Add PLUS Expr'
        t[0] = Node('+').addkid(t[1]).addkid(t[3])

    def p_Add2(self, t):
        'Add : Expr'
        t[0] = t[1]

    def p_Expr1(self, t):
        'Expr : INT_VAL'
        t[0] = Node('INT').addkid(t[1])

    def p_Expr2(self, t):
        'Expr : LPAREN Div RPAREN'
        t[0] = t[2]

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        2*3/(4-5*(12*32-15))


    ''', lexer=Lexer()).dotty()
