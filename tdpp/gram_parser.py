#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from ply import lex, yacc
from gram_lexer import Lexer, tokens
from collections import MutableMapping

class Symbol(object):

    def __init__(self, sym, terminal, empty, eos):
        self.sym = sym
        self.terminal = terminal
        self.empty = empty
        self.eos = eos

    def __tuple__(self):
        return (self.sym, self.terminal, self.empty, self.eos)

    def __eq__(self, b):
        if b is None: return False
        if isinstance(b, Symbol):
            return self.__tuple__() == b.__tuple__()
        return False

    def __ne__(self, b):
        return not self.__eq__(b)

    def __hash__(self):
        return hash(self.__tuple__())

    def __repr__(self):
        if self.eos: return '<EoS>'
        if self.empty: return '<EmptyString>'
        if self.terminal: return '<Terminal %s>' % self.sym
        return '<NonTerminal %s>' % self.sym

def Terminal(sym):
    return Symbol(sym, True, False, False)
def EmptyString():
    return Symbol('e', True, True, False)
def EoS():
    return Symbol('e', True, False, True)
def NonTerminal(sym):
    return Symbol(sym, False, False, False)


class Productions(MutableMapping):

    def __init__(self, tokens, *args, **kwargs):
        super(Productions, self).__init__(*args, **kwargs)
        self.productions = dict()
        self.order = list()
        self.tokens = tokens

    def __setitem__(self, key, value):
        if key.sym not in self.productions:
            self.productions[key.sym] = list()
            self.order.append(key)
        self.productions[key.sym].append(tuple(value))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.productions[self.order[key].sym]
        return self.productions[key.sym]

    def __delitem__(self, key):
        del self.productions[key.sym]
        self.order.remove(key)

    def __iter__(self):
        for key in self.order:
            yield key

    def __len__(self):
        return len(self.order)

    def __repr__(self): return repr(self.productions)


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
        self.symbols = set()
        self.non_terminals = set()
        self.tokens = set(tokens)
        self.productions = Productions(tokens)

    def addproduction(self, nt, p):
        self.productions[NonTerminal(nt)] = p

    def p_Start(self, t):
        'Start : Productions'
        tokens = self.symbols - self.non_terminals
        if not (tokens <= self.tokens):
            raise Exception, "Non-terminals %s not defined" % str(list(tokens - self.tokens))
        t[0] = self.productions

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

    def p_Symbol2(self, t):
        'Symbol : E'
        t[0] = EmptyString()

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


    p = parse(['NAME', 'LPAREN', 'RPAREN'], '''
Call        : NAME Call'
Call'       : LPAREN Call''
Call''      : e
Call''      : RPAREN
Call''      : NAME RPAREN
    ''')
    print p
    print p.order

