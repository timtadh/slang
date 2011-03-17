#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from ply import lex, yacc
from ply.lex import Token
from ast import Node

class Symbol(object):

    def __init__(self, sym):
        self.sym = sym

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.sym)

class Terminal(Symbol): pass
class NonTerminal(Symbol): pass

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

    def __new__(cls, tokens, **kwargs):
        ## Does magic to allow PLY to do its thing.-
        self = super(Parser, cls).__new__(cls, **kwargs)
        self.yacc = yacc.yacc(module=self, **kwargs)
        self.__init__(tokens)
        return self.yacc

    def __init__(self, tokens):
        self.order = list()
        self.symbols = set()
        self.non_terminals = set()
        self.tokens = set(tokens)
        self.productions = dict()

    def addproduction(self, nt, p):
        if nt not in self.productions:
            self.productions[nt] = list()
            self.order.append(NonTerminal(nt))
        self.productions[nt].append(tuple(p))

    def p_Start(self, t):
        'Start : Productions'
        tokens = self.symbols - self.non_terminals
        if self.tokens != tokens:
            raise Exception, "Non-terminals %s not defined" % str(list(tokens - self.tokens))
        t[0] = tuple(self.order), tuple(self.symbols), self.productions

    def p_Productions1(self, t): 'Productions : Productions Production'
    def p_Productions2(self, t): 'Productions : Production'

    def p_Production(self, t):
        'Production : NAME COLON Symbols NL'
        self.non_terminals.add(t[1])
        self.symbols.add(t[1])
        self.addproduction(t[1], t[3])

    def p_Symbols1(self, t):
        'Symbols : Symbols Symbol'
        t[0] = t[1] + [ t[2] ]

    def p_Symbols2(self, t):
        'Symbols : Symbol'
        t[0] = [ t[1] ]

    def p_Symbol1(self, t):
        'Symbol : NAME'
        self.symbols.add(t[1])
        if t[1] in self.tokens:
            t[0] = Terminal(t[1])
        else:
            t[0] = NonTerminal(t[1])
        #t[0] = t[1]

    def p_Symbol2(self, t):
        'Symbol : E'
        t[0] = Terminal('e')

    def p_error(self, t):
        raise Exception, "Error %s" % t


def parse(tokens, grammar):
    return Parser(tokens).parse(grammar, lexer=Lexer())

if __name__ == '__main__':
    lexer = Lexer()
    lexer.input('''
        Hello : haae awoief
        asdf : awoef aWEa
        Hello : aeoifhnawe
    ''')
    #print [x for x in lexer]


    order, syms, p = parse(['NAME', 'LPAREN', 'RPAREN'], '''
Call        : NAME Call'
Call'       : LPAREN Call''
Call''      : RPAREN
Call''      : NAME RPAREN
    ''')
    print order
    print syms
    print p

