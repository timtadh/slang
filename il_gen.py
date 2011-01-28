#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
from table import SymbolTable
import il

class generate(object):

    def __new__(cls, root):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        r = self.Stmts(root)
        r += [ il.Inst(il.PRNT, r[-1].result, 0, 0)]
        print r
        return r

    def __init__(self):
        self.fcount = 0
        self.tcount = 0
        self.functions = SymbolTable()
        self.objs = SymbolTable()

    def tmp(self):
        self.tcount += 1
        return 't%i' % self.tcount

    def Stmts(self, node):
        assert node.label == 'Stmts'
        code = list()
        for c in node.children:
            if c.label == 'Assign':
                code += self.Assign(c)
            elif c.label == 'Expr':
                code += self.Expr(c)
            else:
                raise Exception, c.label
        return code

    def Assign(self, node):
        assert node.label == 'Assign'
        name = node.children[0]
        c = node.children[1]
        if c.label == 'Expr':
            code = self.Expr(c)
        elif c.label == 'Func':
            self.functions[name] = None
            func = self.Func(c)
            self.functions[name] = func
            code = list()
        else:
            raise Exception, c.label
        if code: self.objs[name] = code[-1].result
        return code

    def Func(self, node):
        assert node.label == 'Func'
        self.objs = self.objs.push()
        self.functions = self.functions.push()

        code = list()

        for c in node.children:
            if c.label == 'DParams':
                code += self.DParams(node.children[0])
            elif c.label == 'Stmts':
                code += self.Stmts(c)
            elif c.label == 'Return':
                code += self.Return(c)
            else:
                raise Exception, c.label

        self.objs = self.objs.pop()
        self.functions = self.functions.pop()

        return code

    def Return(self, node):
        assert node.label == 'Return'
        code = list()
        if node.children:
            if node.children[0].label == 'Expr':
                code += self.Expr(node.children[0])
                t = code[-1].result
                if code[-1].op == 'USE': code = code[:-1]
                code += [ il.Inst(il.OPRM, t, 0, 0) ]
            else:
                raise Exception
        code += [ il.Inst(il.RTRN, 0, 0, 0) ]
        return code

    def DParams(self, node):
        assert node.label == 'DParams'
        code = list()
        for i, c in enumerate(node.children):
            t = self.tmp()
            self.objs[c] = t
            code.append(il.Inst(il.GPRM, i, 0, t))
        return code

    def Expr(self, node):
        if node.label == 'Expr':
            c = node.children[0]
        else:
            c = node
        if c.label == 'INT':
            return self.Int(c.children[0])
        elif c.label == '/' or c.label == '*' or c.label == '-' or c.label == '+':
            return self.Op(c)
        elif c.label == 'NAME':
            return [ il.Inst('USE', 0, 0, self.objs[c.children[0]]) ]
        elif c.label == 'Expr':
            return self.Expr(c)
        else:
            raise Exception, 'Unexpected Node %s' % str(c)

    def Op(self, node):
        ops = {'/':'DIV', '*':'MUL', '-':'SUB', '+':'ADD'}
        A = self.Expr(node.children[0])
        B = self.Expr(node.children[1])
        ar = A[-1].result
        br = B[-1].result
        if A[-1].op == 'USE': A = A[:-1]
        if B[-1].op == 'USE': B = B[:-1]
        return A + B + [
            il.Inst(il.ops[ops[node.label]],
            ar,
            br,
            self.tmp())
        ]

    def Int(self, node):
        return [ il.Inst(il.IMM, node, 0, self.tmp()) ]


    # ------------------------------------------------------------------------ #


if __name__ == '__main__':

    print il.run(generate(Parser().parse(''' a = 2*3/(4-5*(12*32-15)) ''', lexer=Lexer())))
    print il.run(generate(Parser().parse(''' a= 1 + 2 - (3+4) ''', lexer=Lexer())))
    print il.run(generate(Parser().parse(''' a=2 ''', lexer=Lexer())))
    print il.run(generate(Parser().parse(''' x = (2*3/(4-5*(12*32-15)))
        y = 0
        z = 0
        w = x + y + z''', lexer=Lexer())))
    print generate(Parser().parse('''
        f = func(a, b) { c = a + b return c }
        f(1,2)
    ''', lexer=Lexer()))

