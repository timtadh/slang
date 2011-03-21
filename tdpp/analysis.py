#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from gram_parser import parse, EmptyString, NonTerminal

def first(productions, sym):
    if sym.terminal: return set([sym])
    symbols = set()
    for p in productions[sym]:
        all_e = True
        for psym in p:
           psym_first = first(productions, psym)
           symbols |= psym_first
           if EmptyString() not in psym_first:
               all_e = False
               break
        if all_e:
            symbols.add(EmptyString())
    return symbols

if __name__ == '__main__':
    from ply import lex
    from ply.lex import Token

    reserved = dict(
        (word.lower(), word) for word in (
            'NUMBER',
        )
    )

    tokens = reserved.values() + [
        'SLASH', 'STAR', 'DASH', 'PLUS', 'LPAREN', 'RPAREN'
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
        E : T E'
        E' : PLUS T E'
        #E' : DASH T E'
        E' : e
        T : F T'
        T' : STAR F T'
        #T' : SLASH F T'
        T' : e
        F : NUMBER
        F : LPAREN E RPAREN
    '''

    lexer = Lexer()
    lexer.input('6+7')

    productions = parse(tokens, grammar)
    for k,v in productions.iteritems():
        print k
        for p in v:
            print ' '*4, p
        print ' '*4, 'first', tuple(first(productions, k))
    #print 'first E', first(productions, NonTerminal("E"))
    #print 'first T', first(productions, NonTerminal("T"))
    #print 'first F', first(productions, NonTerminal("F"))
    assert first(productions, NonTerminal("E")) == first(productions, NonTerminal("T")) == first(productions, NonTerminal("F"))
    #print "first E'", first(productions, NonTerminal("E'"))
    #print "first T'", first(productions, NonTerminal("T'"))

