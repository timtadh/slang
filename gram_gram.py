#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from ply import lex, yacc
from ply.lex import Token
from ast import Node

reserved = dict(
    (word.lower(), word) for word in (
        'E',
    )
)

tokens = reserved.values() + [
    'COLON', 'NAME', 'NL'
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
        self.col = False
        return self.lexer

    tokens = tokens

    name = '(' + L + ')((' + L + ')|(' + D + '))*(\')*'
    @Token(name)
    def t_NAME(self, token):
        if token.value in reserved: token.type = reserved[token.value]
        else: token.type = 'NAME'
        return token

    @Token(r'\n+')
    def t_NL(self, token):
        token.lexer.lineno += token.value.count("\n")
        token.type = 'NL'
        r = None
        if self.col: r = token
        self.col = False
        return r

    @Token(r':')
    def t_COLON(self, token):
        self.col = True
        return token

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


## If you are confused about the syntax in this file I recommend reading the
## documentation on the PLY website to see how this compiler compiler's syntax
## works.
class Parser(object):

    tokens = tokens
    precedence = (
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
        'Start : Productions'
        t[0] = Node('Productions', t[1])

    def p_Productions1(self, t):
        'Productions : Productions Production'
        t[0] = t[1] + [ t[2] ]

    def p_Productions2(self, t):
        'Productions : Production'
        t[0] = [ t[1] ]

    def p_Production(self, t):
        'Production : NAME COLON Symbols NL'
        t[0] = (
            Node('Production')
                .addkid(Node(t[1]))
                .addkid(Node('Rule', t[3]))
        )

    def p_Symbols1(self, t):
        'Symbols : Symbols Symbol'
        t[0] = t[1] + [ t[2] ]

    def p_Symbols2(self, t):
        'Symbols : Symbol'
        t[0] = [ t[1] ]

    def p_Symbol1(self, t):
        'Symbol : NAME'
        t[0] = Node('Symbol').addkid(t[1])

    def p_Symbol2(self, t):
        'Symbol : E'
        t[0] = Node('Symbol')

    def p_error(self, t):
        raise Exception, "Error %s" % t


if __name__ == '__main__':
    lexer = Lexer()
    lexer.input('''
        Hello : haae awoief
        asdf : awoef aWEa
        Hello : aeoifhnawe
    ''')
    #print [x for x in lexer]


    print Parser().parse('''
Call        : NAME Call'
Call'       : LPAREN Call''
Call''      : RPAREN
Call''      : Params RPAREN
    ''', lexer=Lexer()).dotty()
