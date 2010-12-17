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
    precedence = (
        ('left', 'EQUAL'),
    )

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
        'Start : Block'
        t[0] = t[1]

    def p_Block1(self, t):
        'Block : Block Stmt'
        t[0] = t[1].addkid(t[2])

    def p_Block2(self, t):
        'Block : Stmt'
        t[0] = Node('Block').addkid(t[1])

    def p_Stmt1(self, t):
        'Stmt : NAME COLON EQUAL FUNC LPAREN Dparams RPAREN LCURLY Block Return RCURLY'
        t[0] = (
            Node('Assign')
                .addkid(
                    Node('NAME')
                        .addkid(Node(t[1]))
                ).addkid(
                    Node('Func')
                        .addkid(t[6])
                        .addkid(t[9])
                        .addkid(t[10])
                )
        )

    def p_Stmt2(self, t):
        'Stmt : NAME COLON EQUAL FUNC LPAREN RPAREN LCURLY Block Return RCURLY'
        t[0] = (
            Node('Assign')
                .addkid(
                    Node('NAME')
                        .addkid(Node(t[1]))
                ).addkid(
                    Node('Func')
                        .addkid(t[8])
                        .addkid(t[9])
                )
        )

    def p_Stmt3(self, t):
        'Stmt : Dparams EQUAL Call'
        t[0] = Node('Assign').addkid(t[1]).addkid(t[3])

    def p_Stmt4(self, t):
        'Stmt : Call'
        t[0] = t[1]

    def p_Return1(self, t):
        'Return : RETURN Params'
        t[0] = Node('Return').addkid(t[2])

    def p_Return2(self, t):
        'Return : CONTINUE Call'
        t[0] = Node('Continue').addkid(t[2])

    def p_Call1(self, t):
        'Call : NAME LPAREN Params RPAREN'
        t[0] = Node('Call').addkid(Node('NAME').addkid(Node(t[1]))).addkid(t[3])

    def p_Call2(self, t):
        'Call : NAME LPAREN RPAREN'
        t[0] = Node('Call').addkid(Node('NAME').addkid(Node(t[1])))

    def p_Dparams1(self, t):
        'Dparams : Dparams COMMA NAME'
        t[0] = t[1].addkid(Node('NAME').addkid(Node(t[3])))

    def p_Dparams2(self, t):
        'Dparams : NAME'
        t[0] = Node('Dparams').addkid(Node('NAME').addkid(Node(t[1])))

    def p_Params1(self, t):
        'Params : Params COMMA Value'
        t[0] = t[1].addkid(t[3])

    def p_Params2(self, t):
        'Params : Value'
        t[0] = Node('Params').addkid(t[1])

    def p_Value1(self, t):
        'Value : NAME'
        t[0] = Node('NAME').addkid(Node(t[1]))

    def p_Value2(self, t):
        'Value : INT'
        t[0] = Node('INT').addkid(Node(t[1]))

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        f := func(a, b) {
            c = add(a,b)
            return c, b
        }
        r, r2 = f(2,3)
        print(r)
        exit()
    ''', lexer=Lexer()).dotty()
