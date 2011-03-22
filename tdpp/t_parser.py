#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from parser import BaseParser
from ply import lex, yacc
from ply.lex import Token

reserved = dict(
    (word.lower(), word) for word in (
        'NUMBER',
    )
)

tokens = reserved.values() + [
    'SLASH', 'DASH',
    'STAR', 'PLUS', 'LPAREN', 'RPAREN'
]

# Common Regex Parts

D = r'[0-9]'
L = r'[a-zA-Z_]'
H = r'[a-fA-F0-9]'
E = r'[Ee][+-]?(' + D + ')+'


## Normally PLY works at the module level. I perfer having it encapsulated as
## a class. Thus the strange construction of this class in the new method allows
## PLY to do its magic.
class Lexer(object):

    def __new__(cls, **kwargs):
        self = super(Lexer, cls).__new__(cls, **kwargs)
        self.lexer = lex.lex(object=self, **kwargs)
        return self.lexer

    tokens = tokens

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_SLASH = r'\/'
    t_STAR = r'\*'
    t_DASH = r'\-'
    t_PLUS = r'\+'


    const_hex = '0[xX](' + H + ')+'
    @Token(const_hex)
    def t_CONST_HEX(self, token):
        token.type = 'NUMBER'
        token.value = int(token.value, 16)
        return token

    const_dec_oct = '(' + D + ')+'
    @Token(const_dec_oct)
    def t_CONST_DEC_OCT(self, token):
        token.type = 'NUMBER'
        if (len(token.value) > 1 and token.value[0] == '0'
            or (token.value[0] == '-' and token.value[1] == '0')):
            token.value = int(token.value, 8)
        else:
            token.value = int(token.value, 10)
        return token

    def t_error(self, t):
        raise Exception, t

grammar = '''
    Expr : Term Expr';
    Expr' : PLUS Term Expr';
    Expr' : DASH Term Expr';
    Expr' : e;
    Term : Factor Term';
    Term' : STAR Factor Term';
    Term' : SLASH Factor Term';
    Term' : e;
    Factor : NUMBER;
    Factor : LPAREN Expr RPAREN;
'''

class Parser(BaseParser):

    tokens = tokens

    def evalop(self, op, a, b):
        print op, a, b
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a / b
        raise Exception

    @BaseParser.production("Start : Expr")
    def Start(self, start, expr):
        return expr

    @BaseParser.production("Term : Factor Term'")
    @BaseParser.production("Expr : Term Expr'")
    def ExprTerm(self, expr_, b, extra):
        if extra is not None:
            b = self.evalop(extra[0], b, extra[1])
        return b

    @BaseParser.production("Expr' : DASH Term Expr'")
    @BaseParser.production("Expr' : PLUS Term Expr'")
    @BaseParser.production("Term' : SLASH Factor Term'")
    @BaseParser.production("Term' : STAR Factor Term'")
    def Op(self, nt, op, b, extra):
        if extra is not None:
            b = self.evalop(extra[0], b, extra[1])
        return op, b

    @BaseParser.production("Term' : e")
    @BaseParser.production("Expr' : e")
    def Empty(self, *args): pass

    @BaseParser.production("Factor : NUMBER")
    def Factor1(self, factor, number):
        return number

    @BaseParser.production("Factor : LPAREN Expr RPAREN")
    def Factor2(self, factor, lparen, expr, rparen):
        return expr


lexer = Lexer()
def Lex(string):
    lexer.input(string)
    for t in lexer:
        yield t

parser = Parser(Lex)

for nt in parser.productions.order:
    print nt

print parser.parse('7*4*3')
