#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from parser import BaseParser

class token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return str(self.value)

def Lex(inpt):
    digits = list()
    for x in inpt:
        if x.isdigit():
            digits.append(x)
        elif digits:
            yield token('NUMBER', int(''.join(digits)))
            digits = list()

        if x == ' ': continue
        elif x == '+': yield token('PLUS', x)
        elif x == '-': yield token('DASH', x)
        elif x == '*': yield token('STAR', x)
        elif x == '/': yield token('SLASH', x)
        elif x == '(': yield token('LPAREN', x)
        elif x == ')': yield token('RPAREN', x)
        elif not x.isdigit():
            raise Exception, 'Unknown character! %s' % (x)
    if digits:
        yield token('NUMBER', int(''.join(digits)))

class Parser(BaseParser):

    tokens = [ 'NUMBER', 'SLASH', 'DASH', 'STAR', 'PLUS', 'LPAREN', 'RPAREN' ]

    def evalop(self, op, a, b):
        #return op, a, b
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a / b
        raise Exception

    @BaseParser.production("Start : Expr")
    def Start(self, start, expr):
        return expr

    @BaseParser.production("Term : Factor Term'")
    @BaseParser.production("Expr : Term Expr'")
    def ExprTerm(self, expr_, b, extra):
        print 'et>', b, extra
        if extra is not None:
            b = self.evalop(extra[0], b, extra[1])
            #print ' '*4, b
            if len(extra) == 3:
                #print ' '*4, extra[2]
                return self.ExprTerm(None, b, extra[2])
        return b

    @BaseParser.productions('''
        Expr' : DASH Term Expr';
        Expr' : PLUS Term Expr';
        Term' : SLASH Factor Term';
        Term' : STAR Factor Term';
    ''')
    def Op(self, nt, op, b, extra):
        print 'op>', op, b, extra
        if extra is not None:
            if len(extra) == 2:
                return op.value, b, (extra[0], extra[1])
            return op.value, b, (extra[0], extra[1], extra[2])
        return op.value, b

    @BaseParser.production("Term' : e")
    @BaseParser.production("Expr' : e")
    def Empty(self, *args): pass

    @BaseParser.production("Factor : NUMBER")
    def Factor1(self, factor, number):
        return number.value

    @BaseParser.production("Factor : LPAREN Expr RPAREN")
    def Factor2(self, factor, lparen, expr, rparen):
        return expr

parser = Parser(Lex, debug=True)
def test(expr):
    p = parser.parse(expr)
    assert eval(expr) == p
    print p
#print parser.parse('7*4*3')
test('9*4/(4*2+4)*6/8')
