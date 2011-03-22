#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools
from ply import lex, yacc
from gram_lexer import Lexer, tokens
from collections import MutableMapping

class Symbol(object):

    def __init__(self, sym, terminal, empty, eos):
        self.sym = sym
        self.terminal = terminal
        self.empty = empty
        self.eos = eos
        self.value = None

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
        if self.terminal and self.value: return '<Terminal %s %s>' % (self.sym, self.value)
        if self.terminal: return '<Terminal %s>' % self.sym
        return '<NonTerminal %s>' % self.sym

def Terminal(sym):
    return Symbol(sym, True, False, False)
def EmptyString():
    return Symbol('e', True, True, False)
def EoS():
    return Symbol('$', True, False, True)
def NonTerminal(sym):
    return Symbol(sym, False, False, False)


class Productions(MutableMapping):

    def __init__(self, tokens, *args, **kwargs):
        super(Productions, self).__init__(*args, **kwargs)
        self.productions = dict()
        self.functions = dict()
        self.order = list()
        self.tokens = tokens
        self.index = dict()

    def containing(self, sym):
        if sym not in self.index: return
        for p in self.index[sym]:
            yield p

    def __ior__(self, b):
        for k,v in b.iteritems():
            for p in v:
                self[k] = p
            if k not in b.functions: continue
            if k in self.functions: offset = len(self.functions[k])
            else: offset = 0
            for i, f in enumerate(b.functions[k]):
                self.addfunc(k, offset+i, f)

        return self

    def addfunc(self, key, i, func):
        assert len(self[key])-1 == i
        if key not in self.functions:
            self.functions[key] = list()
        assert len(self.functions[key]) == i
        self.functions[key].append(func)

    def getfunc(self, key, i):
        return self.functions[key][i]

    def __setitem__(self, key, value):
        if key.sym not in self.productions:
            self.productions[key.sym] = list()
            self.order.append(key)
        if not isinstance(value, tuple): value = tuple(value)
        if value in self.productions[key.sym]: return
        self.productions[key.sym].append(value)
        for sym in value:
            if sym not in self.index:
                self.index[sym] = list()
            self.index[sym].append((key, value))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.order[key]
        return self.productions[key.sym]

    def __delitem__(self, key):
        for p in self.productions[key.sym]:
            for sym in p:
                if sym in self.index:
                    self.index[sym].remove((key, p))
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
        self.yacc = yacc.yacc(module=self, tabmodule="gram_parser_tab", debug=0, **kwargs)
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
        #if not (tokens <= self.tokens):
            #raise Exception, "Non-terminals %s not defined" % str(list(tokens - self.tokens))
        t[0] = self.productions

    def p_Productions1(self, t): 'Productions : Productions Production'
    def p_Productions2(self, t): 'Productions : Production'

    def p_Production(self, t):
        'Production : NAME COLON Symbols END'
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

    #import pdb
    #pdb.set_trace()
    return Parser(tokens).parse(grammar, lexer=Lexer())

if __name__ == '__main__':
    lexer = Lexer()
    lexer.input('''
        Hello : haae awoief
        asdf : awoef aWEa
        Hello : aeoifhnawe
    ''')
    #print [x for x in lexer]

    tokens = ['PLUS', 'LPAREN', 'RPAREN']
    PARSE = functools.partial(parse, tokens)

    p = PARSE("Expr' : PLUS Factor Expr';")
    p.addfunc(p[0], 0, 1)
    print p[0], p[p[0]][0], p.functions[p[0]]
    p2 = PARSE("Expr' : DASH Factor Expr';")
    p2.addfunc(p[0], 0, 2)
    p |= p2
    print p
    print p[0], p[p[0]][0], p.functions[p[0]]
    print p.getfunc(p[0], 0)
    print p.getfunc(p[0], 1)
    print p.order

