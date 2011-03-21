#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from gram_parser import parse, EmptyString, EoS,  NonTerminal, Terminal
import analysis
import parser

import functools
from ply import lex
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
    Expr : Term Expr'
    Expr' : PLUS Term Expr'
    Expr' : DASH Term Expr'
    Expr' : e
    Term : Factor Term'
    Term' : STAR Factor Term'
    Term' : SLASH Factor Term'
    Term' : e
    Factor : NUMBER
    Factor : LPAREN Expr RPAREN
'''


productions = parse(tokens, grammar)

def FIRST(sym):
    if hasattr(sym, 'sym'):
        return analysis.first(productions, sym)
    return analysis.first(productions, NonTerminal(sym))
def FOLLOW(sym):
    if hasattr(sym, 'sym'):
        return analysis.follow(productions, sym)
    return analysis.follow(productions, NonTerminal(sym))

def t_print():
    for k,v in productions.iteritems():
        print k
        for p in v:
            print ' '*4, p
        print ' '*4, 'first', tuple(FIRST(k))
        print ' '*4, 'follow', tuple(FOLLOW(k))


def t_first():
    assert FIRST("E") == FIRST("T") == FIRST("F")
    assert FIRST('E') == set([Terminal('LPAREN'), Terminal('NUMBER')])
    assert FIRST("E'") == set([Terminal('PLUS'), Terminal('DASH'), EmptyString()])
    assert FIRST("T'") == set([Terminal('STAR'), Terminal('SLASH'), EmptyString()])

def t_follow():
    assert FOLLOW("E") == FOLLOW("E'") == set([Terminal("RPAREN"), EoS()])
    assert FOLLOW("T") == FOLLOW("T'")
    assert FOLLOW("T") == set([Terminal("DASH"), Terminal("PLUS"), Terminal("RPAREN"), EoS()])
    assert FOLLOW("F") == set([
        Terminal('STAR'), Terminal('SLASH'), Terminal("DASH"), Terminal("PLUS"), Terminal("RPAREN"), EoS()
    ])

def t_check():
    assert analysis.LL1(productions)
    assert not analysis.LL1(parse(tokens, grammar + '\n F : LPAREN NUMBER RPAREN\n'))


def t_build():
    print analysis.build_table(productions, True)

def t_parser():
    lexer = Lexer()
    lexer.input('6+7*4+3*2*(4+3)')
    for c, v in list(parser.parse((t for t in lexer), productions)):
        print "%s:%s" % (c, v)
