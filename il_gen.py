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
        main = self.Stmts(root)
        #print
        print 'main'
        for i in main:
            print ' '*4, i
        for f in self.functions:
            print f
            for i in self.functions[f]:
                print ' '*4, i
            print
            print
        main = self.index_labels(main)
        functions = dict((f, self.index_labels(insts)) for f, insts in self.functions.iteritems())
        return main, functions

    def __init__(self):
        self.fcount = 0
        self.tcount = 0
        self.lcount = 0
        self.functions = dict()
        self.objs = SymbolTable()

    def index_labels(self, insts):
        labels = dict()
        for i, inst in enumerate(insts):
            if inst.label is not None:
                labels[inst.label] = i
        return insts, labels

    def tmp(self):
        self.tcount += 1
        return 't%i' % self.tcount

    def fun(self):
        self.fcount += 1
        return 'f%i' % self.fcount

    def label(self):
        self.lcount += 1
        return 'label_%i' % self.lcount


    def Stmts(self, node):
        assert node.label == 'Stmts'
        code = list()
        for c in node.children:
            if c.label == 'Assign':
                self.PreAssign(c)
        for c in node.children:
            if c.label == 'Assign':
                code += self.Assign(c)
            elif c.label == 'Expr':
                code += self.Expr(c)
            elif c.label == 'Call':
                code += self.Call(c)
            elif c.label == 'Print':
                code += self.Print(c)
            elif c.label == 'If':
                code += self.If(c)
            else:
                raise Exception, c.label
        return code

    def If(self, node):
        assert node.label == 'If'
        code = list()
        cmpexpr = node.children[0].children[0]
        endlabel = self.label()
        thenstmts = self.Stmts(node.children[1])
        thenstmts[0].label = self.label()
        thenstmts += [ il.Inst(il.J, endlabel, 0, 0) ]
        if len(node.children) == 3:
            elsestmts = self.Stmts(node.children[2])
            elsestmts[0].label = self.label()
            elsestmts += [ il.Inst(il.J, endlabel, 0, 0) ]
        else: elsestmts = None

        cmpexpr = self.CmpOp(cmpexpr)
        cmpr = cmpexpr[-1].result

        code += cmpexpr
        code += [ il.Inst(il.BEQZ, cmpr, thenstmts[0].label, 0) ]
        if elsestmts:
            code += [ il.Inst(il.J, elsestmts[0].label, 0, 0) ]
        code += thenstmts
        code += elsestmts
        code += [ il.Inst(il.NOP, 0, 0, 0, endlabel) ]

        return code

    def Print(self, node):
        assert node.label == 'Print'
        c = node.children[0]
        code = list()
        if c.label == 'Expr':
            code += self.Expr(c)
            t = code[-1].result
            if code[-1].op == 'USE': code = code[:-1]
        else:
            raise Exception, c.label
        code += [ il.Inst(il.PRNT, t, 0, 0)]
        return code


    def PreAssign(self, node):
        assert node.label == 'Assign'
        name = node.children[0]
        c = node.children[1]
        if c.label == 'Func':
            c.fun = self.fun()
            self.objs[name] = c.fun

    def Assign(self, node):
        assert node.label == 'Assign'
        name = node.children[0]
        c = node.children[1]
        if c.label == 'Expr':
            code = self.Expr(c)
        elif c.label == 'Func':
            fun = c.fun
            self.functions[fun] = self.Func(c)
            self.objs[name] = fun
            code = list()
        else:
            raise Exception, c.label
        if code: self.objs[name] = code[-1].result
        return code

    def Func(self, node):
        assert node.label == 'Func'
        self.objs = self.objs.push()

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

        return code

    def Return(self, node):
        assert node.label == 'Return'
        code = list()
        if node.children:
            if node.children[0].label == 'Expr':
                code += self.Expr(node.children[0])
                t = code[-1].result
                if code[-1].op == 'USE': code = code[:-1]
                code += [ il.Inst(il.OPRM, 0, t, 0) ]
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
        elif c.label == 'Call':
            return self.Call(c)
        else:
            raise Exception, 'Unexpected Node %s' % str(c)

    def CmpOp(self, node):
        ops = {'==':il.EQ, '=!':il.NE, '<':il.LT, '<=':il.LE, '>':il.GT, '>=':il.GE}
        A = self.Expr(node.children[0])
        B = self.Expr(node.children[1])
        ar = A[-1].result
        br = B[-1].result
        if A[-1].op == 'USE': A = A[:-1]
        if B[-1].op == 'USE': B = B[:-1]
        return A + B + [
            il.Inst(ops[node.label],
            ar,
            br,
            self.tmp())
        ]

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

    def Call(self, node):
        assert node.label == 'Call'
        code = list()
        fun = self.objs[node.children[0]]
        if len(node.children) != 1:
            code += self.Params(node.children[1])
        code += [ il.Inst(il.CALL, fun, 0, 0) ]
        code += [ il.Inst(il.RPRM, 0, 0, self.tmp()) ]
        return code

    def Params(self, node):
        assert node.label == 'Params'
        code = list()
        params = list()
        for c in node.children:
            code += self.Expr(c)
            params.append(code[-1].result)
            if code[-1].op == 'USE': code = code[:-1]
        params.reverse()
        for i, p in enumerate(params):
            code += [ il.Inst(il.IPRM, len(params)-1-i, p, 0) ]
        return code

    def Int(self, node):
        return [ il.Inst(il.IMM, node, 0, self.tmp()) ]


    # ------------------------------------------------------------------------ #


if __name__ == '__main__':

    print il.run(*generate(Parser().parse(''' print 2*3/(4-5*(12*32-15)) ''', lexer=Lexer())))
    print il.run(*generate(Parser().parse(''' print 1 + 2 - (3+4) ''', lexer=Lexer())))
    print il.run(*generate(Parser().parse(''' print 2 ''', lexer=Lexer())))
    print il.run(*generate(Parser().parse(''' x = (2*3/(4-5*(12*32-15)))
        print x
        y = x + 3
        print y
        z = y + 4
        print z
        print x + y + z''', lexer=Lexer())))
    print il.run(*generate(Parser().parse('''
            add = func(a, b) {
                print a
                print b
                _add = func() {
                    return a + b
                }
                c = _add()
                return c
            }
            print add(1, 3)
        ''', lexer=Lexer())))
    print il.run(*generate(Parser().parse('''
                _add = func(a, b) {
                    return a + b
                }
                add = func(f, a, b) {
                    return f(a, b)
                }
                print add(_add, 2, 3)
        ''', lexer=Lexer())))

