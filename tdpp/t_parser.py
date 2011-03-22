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

    @BaseParser.production("Start : Expr")
    def Start(self, *args): pass

    @BaseParser.production("Expr : Term Expr'")
    def Expr(self, *args): pass

    @BaseParser.production("Expr' : PLUS Term Expr'")
    def Expr_1(self, *args): pass

    @BaseParser.production("Expr' : DASH Term Expr'")
    def Expr_2(self, *args): pass

    @BaseParser.production("Expr' : e")
    def Expr_3(self, *args): pass

    @BaseParser.production("Term : Factor Term'")
    def Term(self, *args): pass

    @BaseParser.production("Term' : STAR Factor Term'")
    def Term_1(self, *args): pass

    @BaseParser.production("Term' : SLASH Factor Term'")
    def Term_2(self, *args): pass

    @BaseParser.production("Term' : e")
    def Term_3(self, *args): pass

    @BaseParser.production("Factor : NUMBER")
    def Factor1(self, *args): pass

    @BaseParser.production("Factor : LPAREN Expr RPAREN")
    def Factor2(self, *args): pass

lexer = Lexer()
def Lex(string):
    lexer.input(string)
    for t in lexer:
        yield t

parser = Parser(Lex)

for nt in parser.productions.order:
    print nt
