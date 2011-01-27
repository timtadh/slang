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
        'Start : Block Expr'
        t[0] = t[1]

    def p_Arith1(self, t):
        'Block : Block Stmt'
        t[0] = t[1].addkid(t[2])

    def p_Block2(self, t):
        'Block : Stmt'
        t[0] = Node('Block').addkid(t[1])

    def p_Stmt(self, t):
        'Stmt : NAME EQUAL Expr'
        t[0] = Node('Assign').addkid(t[1]).addkid(t[3])

    def p_Expr1(self, t):
        'Expr : L LPAREN NAME RPAREN LCURLY Block Expr RCURLY '
        t[0] = (
            Node('Func')
                .addkid(Node(t[3]))
                .addkid(t[6])
                .addkid(t[7])
        )

    def p_Expr2(self, t):
        'Expr : L LPAREN NAME RPAREN LCURLY Expr RCURLY '
        t[0] = (
            Node('Func')
                .addkid(Node(t[3]))
                .addkid(t[6])
        )

    def p_Expr3(self, t):
        'Expr : Value'
        t[0] = t[1]

    def p_Call(self, t):
        'Call : NAME LPAREN Value RPAREN'
        t[0] = Node('Call').addkid(Node(t[1])).addkid(t[3])

    def p_Value1(self, t):
        'Value : NAME'
        t[0] = Node('NAME').addkid(Node(t[1]))

    def p_Value2(self, t):
        'Value : INT_VAL'
        t[0] = Node('INT').addkid(Node(t[1]))

    def p_Value3(self, t):
        'Value : Call'
        t[0] = t[1]

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        c0 = l(s) { 0 }
        S  = l(n) {
            }
        c0S = c0(S)
        c1 = c0S(c0)


    ''', lexer=Lexer()).dotty()
