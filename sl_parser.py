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
        'Start : Stmts'
        t[0] = t[1]

    def p_Stmts1(self, t):
        'Stmts : Stmts Stmt'
        t[0] = t[1].addkid(t[2])

    def p_Stmts2(self, t):
        'Stmts : Stmt'
        t[0] = Node('Stmts').addkid(t[1])

    def p_Stmt1(self, t):
        'Stmt : Expr'
        t[0] = t[1]

    def p_Stmt2(self, t):
        'Stmt : NAME EQUAL Expr'
        t[0] = Node('Assign').addkid(t[1]).addkid(t[3])

    def p_Stmt3(self, t):
        'Stmt : Call'
        t[0] = t[1]

    def p_Stmt4(self, t):
        'Stmt : NAME EQUAL Call'
        t[0] = Node('Assign').addkid(t[1]).addkid(t[3])

    def p_Expr(self, t):
        'Expr : Div'
        t[0] = Node('Expr').addkid(t[1])

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
        'Add : Add PLUS Stmt'
        t[0] = Node('+').addkid(t[1]).addkid(t[3])

    def p_Add2(self, t):
        'Add : Atomic'
        t[0] = t[1]

    def p_Atomic1(self, t):
        'Atomic : Value'
        t[0] = t[1]

    def p_Atomic2(self, t):
        'Atomic : LPAREN Expr RPAREN'
        t[0] = t[2]

    def p_Value1(self, t):
        'Value : INT_VAL'
        t[0] = Node('INT').addkid(t[1])

    def p_Value2(self, t):
        'Value : NAME'
        t[0] = Node('NAME').addkid(t[1])

    def p_Value3(self, t):
        'Value : Call'
        t[0] = t[1]

    def p_Call1(self, t):
        'Call : NAME LPAREN RPAREN'
        t[0] = Node('Call').addkid(t[1])

    def p_Call2(self, t):
        'Call : NAME LPAREN Params RPAREN'
        t[0] = Node('Call').addkid(t[1]).addkid(t[3])

    def p_Params1(self, t):
        'Params : Params COMMA Expr'
        t[0] = t[1].addkid(t[3])

    def p_Params2(self, t):
        'Params : Expr'
        t[0] = Node('Params').addkid(t[1])

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        x = 2*3/(4-5*(12*32-15))
        y = x+3
        z = f(x, y, 3+4)


    ''', lexer=Lexer()).dotty()
