#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools
from sl_lexer import Lexer
from gram_gram import parse as gram_parse
from gram_gram import Terminal, NonTerminal

def first(tokens, productions, sym):
    if isinstance(sym, Terminal) or sym == 'e': return set([sym])
    symbols = set()
    for p in productions[sym.sym]:
        if Terminal('e') in p:
            print sym.sym, p
        all_e = True
        for s in p:
            syms = first(tokens, productions, s)
            symbols |= syms
            #print syms
            if Terminal('e') not in syms:
                all_e = False
                break
        if all_e:
            symbols.add(Terminal('e'))
    return symbols

def follow(order, productions, sym):
    symbols = set()
    if sym == order[0]: symbols.add('$')
    tsym = ('nt', sym)
    for nt in order:
        for p in productions[nt]:
            if tsym in p:
                i = p.index(tsym)
                if i+1 < len(p):
                    f = first(p[i+1][1])
                    if 'e' in f:
                        f.remove('e')
                        symbols |= follow(nt)
                    symbols |= f
                elif i+1 == len(p) and sym != nt:
                    symbols |= follow(nt)
    return symbols

def build(tokens, order, symbols, productions):
    FIRST = functools.partial(first, tokens, productions)
    FOLLOW = functools.partial(first, order, productions)

    M = dict()
    for nt in productions.keys():
        for t in tokens + [ 'e' ]:
            M[(nt, t)] = set()
        M[(nt, '$')] = set()

    for nt in order:
        for p in productions[nt.sym]:
            s = p[0]
            f = FIRST(s)
            for sym in f:
                #print sym
                if sym.sym == 'e': continue
                if productions.has_key(sym.sym): continue
                M[(nt.sym, sym.sym)] |= set([(nt.sym, p)])
            if 'e' in f:
                for sym in FOLLOW(nt):
                    #print '------->', sym
                    M[(nt.sym, sym.sym)] |= set([(nt.sym, p)])
    #for nt in order:
        #for t in tokens:
            #if M[(nt.sym, t)] == set():
                #print (nt.sym, t)
            #for p in list(M[(nt.sym, t)]):
                #print (nt.sym, t), p[0], '::=', ' '.join(x.sym for x in p[1])

        #if M[(nt.sym, '$')] == set():
            #print (nt.sym, '$')
        #for p in list(M[(nt.sym, '$')]):
            #print (nt.sym, '$'), p[0], '::=', ' '.join(x for x in p[1])
    return M

def parse(inpt, tokens, grammar):
    def next():
        try: return inpt.next()
        except: return '$'

    order, symbols, productions = gram_parse(tokens, grammar)
    M = build(tokens, order, symbols, productions)

    stack = list()
    a = next()
    stack.append('$')
    stack.append(order[0])
    X = stack[-1]
    while X != '$':
        if a != '$': A = a.type
        else: A = a
        print X, A
        if X.sym == A:
            yield a
            stack.pop()
            a = next()
        elif isinstance(X, Terminal):
            raise Exception, "error 1"
        elif (X.sym, A) not in M:
            raise Exception, "%s not in M" % ((X.sym, A),)
        elif M[(X.sym, A)] == 'error':
            raise Exception, "error 2"
        elif M[(X.sym, A)] != set():
            yield X
            stack.pop()
            productions = list(M[(X.sym, A)])
            for p in productions:
                syms = list(p[1])
                syms.reverse()
                for s in syms:
                    if s == 'e': continue
                    stack.append(s)
        else:
            raise SyntaxError, A
        X = stack[-1]

if __name__ == '__main__':

    tokens = ['NAME', 'LPAREN', 'RPAREN', 'INT_VAL', 'FUNC', 'RCURLY', 'EQUAL', 'DASH', 'LCURLY', 'STAR', 'PLUS', 'SLASH', 'PRINT', 'RETURN', 'COMMA']
    grammar = '''Start       : Stmts

Stmts       : Stmt Stmts'
Stmts'      : Stmt Stmts'
Stmts'      : e

Stmt        : PRINT Expr
Stmt        : Call
Stmt        : AssignStmt

AssignStmt  : NAME EQUAL Assignable
Assignable  : Expr
Assignable  : Function

Function    : FUNC LPAREN ParamDecl LCURLY FuncBody RCURLY
ParamDecl   : RPAREN
ParamDecl   : DParams RPAREN
FuncBody    : Return
FuncBody    : Stmts Return

Return      : RETURN RetExpr
RetExpr     : Expr
RetExpr     : e

Expr        : AddSub

AddSub      : MulDiv AddSub'
AddSub'     : PLUS MulDiv AddSub'
AddSub'     : DASH MulDiv AddSub'
AddSub'     : e

MulDiv      : Atomic MulDiv'
MulDiv'     : STAR Atomic MulDiv'
MulDiv'     : SLASH Atomic MulDiv'
MulDiv'     : e

Atomic      : Value
Atomic      : LPAREN Expr RPAREN

Value       : INT_VAL
Value       : NameOrCall

NameOrCall  : NAME NameOrCall'
NameOrCall' : Call'
NameOrCall' : e

Call        : NAME Call'
Call'       : LPAREN Call''
Call''      : RPAREN
Call''      : Params RPAREN

Params      : Expr Params'
Params'     : COMMA Expr Params'
Params'     : e

DParams     : NAME DParams'
DParams'    : COMMA NAME DParams'
    '''
    order, syms, productions = gram_parse(tokens, grammar)

    lexer = Lexer()
    lexer.input('''
        print r
    ''')
    inpt = [x for x in lexer]

    for nt in order:
        for p in productions[nt.sym]:
            if Terminal('e') in p: pass
            print nt, p, Terminal('e')

    #print order
    #print syms
    #print p
    #print 'asdfaweofiawefoajiwefoiawjefoaiwjefoawiejfaowiejfoiawejf'
    M = build(tokens, *gram_parse(tokens, grammar))
    #print list(parse(iter(inpt), tokens, grammar))
