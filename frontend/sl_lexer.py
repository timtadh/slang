#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from ply import lex
from ply.lex import Token

reserved = dict(
    (word.lower(), word) for word in (
        'RETURN', 'CONTINUE', 'FUNC', 'INT', 'VAR', 'PRINT', 'IF', 'ELSE',
        'WHILE', 'FOR',
    )
)

tokens = reserved.values() + [
    'NAME', 'INT_VAL', 'COMMA', 'LPAREN', 'RPAREN', 'LCURLY', 'RCURLY', 'EQUAL',
    #'COLON',
    'DOT', 'SLASH', 'STAR', 'DASH', 'PLUS', 'SEMI',
    'EQEQ', 'NQ', 'LT', 'LE', 'GT', 'GE', 'OR', 'AND', 'NOT'
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

    t_EQEQ = r'=='
    t_NQ = r'!='
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'

    t_SLASH = r'\/'
    t_STAR = r'\*'
    t_DASH = r'\-'
    t_PLUS = r'\+'

    t_NOT = r'\!'
    t_AND = r'\&\&'
    t_OR  = r'\|\|'

    t_DOT = r'\.'
    t_SEMI = r'\;'
    t_EQUAL = r'='
    t_COMMA = r','
    #t_COLON = r':'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LCURLY = r'\{'
    t_RCURLY = r'\}'

    name = '(' + L + ')((' + L + ')|(' + D + '))*'
    @Token(name)
    def t_NAME(self, token):
        if token.value in reserved: token.type = reserved[token.value]
        else: token.type = 'NAME'
        return token

    const_hex = '0[xX](' + H + ')+'
    @Token(const_hex)
    def t_CONST_HEX(self, token):
        token.type = 'INT_VAL'
        token.value = int(token.value, 16)
        return token

    const_dec_oct = '(' + D + ')+'
    @Token(const_dec_oct)
    def t_CONST_DEC_OCT(self, token):
        token.type = 'INT_VAL'
        if (len(token.value) > 1 and token.value[0] == '0'
            or (token.value[0] == '-' and token.value[1] == '0')):
            token.value = int(token.value, 8)
        else:
            token.value = int(token.value, 10)
        return token

    @Token(r'\n+')
    def t_newline(self, t):
        t.lexer.lineno += t.value.count("\n")

    @Token(r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)')
    def t_COMMENT(self, token):
        #print token.lexer.lineno, len(token.value.split('\n')), token.value.split('\n')
        lines = len(token.value.split('\n')) - 1
        if lines < 0: lines = 0
        token.lexer.lineno += lines

    # Ignored characters
    t_ignore = " \t"

    def t_error(self, t):
        raise Exception, "Illegal character '%s'" % t
        t.lexer.skip(1)

if __name__ == '__main__':
    lexer = Lexer()
    lexer.input('''
        f = func(a, b) {
            c = add(a,b)
            return c
        }
        r = f(2,3)
        print r
    ''')
    print [x for x in lexer]
