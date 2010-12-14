#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

def operator(f):
    setattr(f, 'operator', None)
    return f


@operator
def add(a):
    def _add(b):
        return a+b
    return _add

@operator
def sub(a):
    def _sub(b):
        return a-b
    return _sub

@operator
def mul(a):
    def _mul(b):
        return a*b
    return _mul

@operator
def div(a):
    def _div(b):
        return a/b
    return _div

@operator
def _str(a):
    return str(a)

@operator
def _print(a):
    print a,
    return a

@operator
def _println(b):
    print b
    return b

ops = dict((name.lstrip('_'), obj)
        for name,obj in locals().iteritems()
        if hasattr(obj, 'operator')
    )

def tokenize(s, ops):
    def typify(s):
        if   s == '(': return ('o_paren', s)
        elif s == ')': return ('c_paren', s)
        elif s in ops: return ('func', ops[s])
        try: return ('int', int(s))
        except:
            return ('str', s)
    return (typify(s) for s in s.split(' '))

def run(tokens):
    def inner(c, tokens):
        objs = list()
        while c[0] != 'c_paren':
            if c[0] == 'o_paren': c, n = expr(c, tokens)
            else:
                n = c[1]
                c = tokens.next()
            objs.append(n)
        assert len(objs) <= 2
        #print objs
        if len(objs) == 1:
            return c, objs[0]
        elif len(objs) == 2:
            r = objs[0](objs[1])
        return c, r
    def expr(c, tokens):
        if c[0] != 'o_paren': raise Exception, 'no open paren'
        c, expr = inner(tokens.next(), tokens)
        if c[0] != 'c_paren': raise Exception, 'no close paren'
        try: c = tokens.next()
        except StopIteration: c = None
        return c, expr
    c, ret = expr(tokens.next(), tokens)
    if c is not None: raise Exception, 'Not all tokens consumed'
    #print
    #print
    #print ret

if __name__ == '__main__':
    run(tokenize('( ( add ( println ( str ( ( sub 1 ) 2 ) ) ) ) ( println hello ) )', ops))
