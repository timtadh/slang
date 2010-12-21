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
        'Start : Block'
        t[0] = t[1]

    def p_Block1(self, t):
        'Block : Block Stmt'
        t[0] = t[1].addkid(t[2])

    def p_Block2(self, t):
        'Block : Stmt'
        t[0] = Node('Block').addkid(t[1])

    def p_Stmt1(self, t):
        'Stmt : Names EQUAL FUNC LPAREN Dparams RPAREN LCURLY Block Return RCURLY'
        if len(t[1].children) != 1:
            raise Exception, (
                'You cannot have more than one return value for'
                ' a function declaration at line %d'
            ) % t.lineno(2)
        t[0] = (
            Node('Assign')
                .addkid(
                    t[1].children[0]
                ).addkid(
                    Node('Func')
                        .addkid(t[5])
                        .addkid(t[8])
                        .addkid(t[9])
                )
        )

    def p_Stmt2(self, t):
        'Stmt : Names EQUAL FUNC LPAREN RPAREN LCURLY Block Return RCURLY'
        if len(t[1].children) != 1:
            raise Exception, (
                'You cannot have more than one return value for'
                ' a function declaration at line %d'
            ) % t.lineno(2)
        t[0] = (
            Node('Assign')
                .addkid(
                    t[1].children[0]
                ).addkid(
                    Node('Func')
                        .addkid(t[7])
                        .addkid(t[8])
                )
        )

    def p_Stmt3(self, t):
        'Stmt : Names EQUAL Call'
        t[0] = Node('Assign').addkid(t[1]).addkid(t[3])

    def p_Stmt4(self, t):
        'Stmt : Call'
        t[0] = t[1]

    def p_Return1(self, t):
        'Return : RETURN Params'
        t[0] = Node('Return')
        for c in t[2].children:
            t[0].addkid(c)

    def p_Return2(self, t):
        'Return : RETURN'
        t[0] = Node('Return')

    def p_Return3(self, t):
        'Return : CONTINUE Call'
        t[0] = Node('Continue').addkid(t[2])

    def p_Call1(self, t):
        'Call : NAME LPAREN Params RPAREN'
        t[0] = Node('Call').addkid(Node('NAME').addkid(Node(t[1]))).addkid(t[3])

    def p_Call2(self, t):
        'Call : NAME LPAREN RPAREN'
        t[0] = Node('Call').addkid(Node('NAME').addkid(Node(t[1])))

    def p_Names1(self, t):
        'Names : Names COMMA NAME'
        t[0] = t[1].addkid(Node('NAME').addkid(Node(t[3])))

    def p_Names2(self, t):
        'Names : NAME'
        t[0] = Node('Names').addkid(Node('NAME').addkid(Node(t[1])))

    def p_Dparams1(self, t):
        'Dparams : Dparams COMMA Decl'
        t[0] = t[1].addkid(t[3])

    def p_Dparams2(self, t):
        'Dparams : Decl'
        t[0] = Node('Dparams').addkid(t[1])

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
        'Value : INT_VAL'
        t[0] = Node('INT').addkid(Node(t[1]))

    def p_Decl(self, t):
        'Decl : NAME Type'
        t[0] = Node('Decl').addkid(Node('NAME').addkid(Node(t[1]))).addkid(t[2])

    def p_Type1(self, t):
        'Type : FUNC'
        t[0] = Node('func')

    def p_Type2(self, t):
        'Type : INT'
        t[0] = Node('int')

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        end = func(r1 int, r2 int) {
            print(r1)
            print(r2)
            exit()
            return
        }
        f = func(a int, b int, end func) {
            c = add(a,b)
            continue end(c, b)
        }
        f(2,3, end)
    ''', lexer=Lexer()).dotty()
