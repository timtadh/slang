#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from ply import yacc
from lexer import tokens, Lexer

## If you are confused about the syntax in this file I recommend reading the
## documentation on the PLY website to see how this compiler compiler's syntax
## works.
class Parser(object):

    def __new__(cls, **kwargs):
        ## Does magic to allow PLY to do its thing.
        self = super(Parser, cls).__new__(cls, **kwargs)
        self.names = dict()
        self.yacc = yacc.yacc(module=self, **kwargs)
        return self.yacc

    tokens = tokens
    precedence = tuple()

    def p_Start(self, t):
        'Start : Block'
        #t[0] = t[1]

    def p_Block1(self, t):
        'Block : Block Stmt'

    def p_Block2(self, t):
        'Block : Stmt'

    def p_Stmt1(self, t):
        'Stmt : NAME EQUAL FUNC LPAREN Dparams RPAREN LCURLY Block Return RCURLY'

    def p_Stmt2(self, t):
        'Stmt : NAME EQUAL FUNC LPAREN RPAREN LCURLY Block Return RCURLY'

    def p_Stmt3(self, t):
        'Stmt : NAME EQUAL Call'

    def p_Stmt4(self, t):
        'Stmt : Call'

    def p_Return1(self, t):
        'Return : RETURN Params'

    def p_Return2(self, t):
        'Return : CONTINUE Call'

    def p_Call1(self, t):
        'Call : NAME LPAREN Params RPAREN'

    def p_Call2(self, t):
        'Call : NAME LPAREN RPAREN'

    def p_Dparams1(self, t):
        'Dparams : Dparams COMMA NAME'

    def p_Dparams2(self, t):
        'Dparams : NAME'

    def p_Params1(self, t):
        'Params : Params COMMA Value'

    def p_Params2(self, t):
        'Params : Value'

    def p_Value1(self, t):
        'Value : NAME'

    def p_Value2(self, t):
        'Value : INT'

    def p_error(self, t):
        raise SyntaxError, "Syntax error at '%s', %s.%s" % (t,t.lineno,t.lexpos)


if __name__ == '__main__':
    print Parser().parse('''
        f = func(a, b) {
            c = add(a,b)
            return c
        }
        r = f(2,3)
        print(r)
    ''', lexer=Lexer())
