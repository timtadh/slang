#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
from table import Symbol, SymbolTable
import il

class generate(object):

    def __new__(cls, root):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        self.Stmts(root, self.top)

        print
        print 'main', self.top.name

        for b in xrange(1, self.bcount+1):
            name = 'b%i' % b
            print "block:", name
            for inst in self.blocks[name].insts:
                print inst
            print
        print

        return self.top.name, self.blocks

    def __init__(self):
        #self.fcount = 0
        self.tcount = 0
        self.bcount = 0

        self.blocks = dict()
        self.top = self.block()

        self.functions = dict()
        self.functions['main'] = [ self.top ]
        self.fstack = [ 'main' ]

        self.objs = SymbolTable()

    def tmp(self):
        self.tcount += 1
        return 't%i' % self.tcount

    def block(self):
        self.bcount += 1
        name = 'b%i' % self.bcount
        self.blocks[name] = il.Block(name)
        return self.blocks[name]

    def Stmts(self, node, blk):
        assert node.label == 'Stmts'
        for c in node.children:
            if c.label == 'Assign':
                self.PreAssign(c)
        for c in node.children:
            if c.label == 'Assign':
                blk = self.Assign(c, blk)
            elif c.label == 'Expr':
                blk = self.Expr(c, blk)
            elif c.label == 'Call':
                blk = self.Call(c, blk)
            elif c.label == 'Print':
                blk = self.Print(c, blk)
            elif c.label == 'If':
                blk = self.If(c, blk)
            else:
                raise Exception, c.label
        return blk

    def If(self, node, blk):
        assert node.label == 'If'

        thenblk = self.block()
        finalblk = self.block()

        cmpr = Symbol('r'+self.tmp(), il.Int())
        blk = self.CmpOp(node.children[0].children[0], cmpr, blk)
        blk.insts += [ il.Inst(il.BEQZ, cmpr, thenblk, 0) ]

        thenblk = self.Stmts(node.children[1], thenblk)
        thenblk.insts += [ il.Inst(il.J, finalblk, 0, 0) ]

        if len(node.children) == 3:
            elseblk = self.block()
            elseblk = self.Stmts(node.children[2], elseblk)
            elseblk.insts += [ il.Inst(il.J, finalblk, 0, 0) ]
            blk.insts += [ il.Inst(il.J, elseblk, 0, 0) ]
        else:
            blk.insts += [ il.Inst(il.J, finalblk, 0, 0) ]

        return finalblk


    def Print(self, node, blk):
        assert node.label == 'Print'

        c = node.children[0]
        if c.label == 'Expr':
            result = Symbol('r'+self.tmp(), il.Int())
            blk = self.Expr(c, result, blk)
        else:
            raise Exception, c.label
        blk.insts += [ il.Inst(il.PRNT, result, 0, 0)]
        return blk


    def PreAssign(self, node):
        assert node.label == 'Assign'
        name = node.children[0]
        c = node.children[1]
        if c.label == 'Func':
            s = Symbol(name, il.Func(None))
            self.objs.add(s)

    def Assign(self, node, blk):
        assert node.label == 'Assign'
        name = node.children[0]
        c = node.children[1]

        if name in self.objs:
            result = self.objs[name]
        else:
            result = Symbol('r'+self.tmp(), il.Int())

        if c.label == 'Expr':
            blk = self.Expr(c, result, blk)
            self.objs[name] = result
        elif c.label == 'Func':
            blk = self.Func(c, name, blk)
        else:
            raise Exception, c.label
        return blk

    def Func(self, node, name, blk):
        assert node.label == 'Func'
        parent_blk = blk
        blk = self.block()
        self.objs[name].type.entry = blk.name

        self.objs = self.objs.push()
        for c in node.children:
            if c.label == 'DParams':
                blk = self.DParams(node.children[0], blk)
            elif c.label == 'Stmts':
                blk = self.Stmts(c, blk)
            elif c.label == 'Return':
                blk = self.Return(c, blk)
            else:
                raise Exception, c.label
        self.objs = self.objs.pop()

        return parent_blk

    def Return(self, node, blk):
        assert node.label == 'Return'
        if node.children:
            if node.children[0].label == 'Expr':
                result = Symbol('r'+self.tmp(), il.Int())
                blk = self.Expr(node.children[0], result, blk)
                blk.insts += [ il.Inst(il.OPRM, 0, result, 0) ]
            else:
                raise Exception
        blk.insts += [ il.Inst(il.RTRN, 0, 0, 0) ]
        return blk

    def DParams(self, node, blk):
        assert node.label == 'DParams'
        for i, c in enumerate(node.children):
            t = Symbol(self.tmp(), il.Int())
            self.objs[c] = t
            blk.insts += [ il.Inst(il.GPRM, i, 0, t) ]
        return blk

    def Expr(self, node, result, blk):
        if node.label == 'Expr':
            c = node.children[0]
        else:
            c = node

        if c.label == 'INT':
            blk = self.Int(c.children[0], result, blk)
        elif c.label == '/' or c.label == '*' or c.label == '-' or c.label == '+':
            blk = self.Op(c, result, blk)
        elif c.label == 'NAME':
            result.type = self.objs[c.children[0]].type
            result.name = self.objs[c.children[0]].name
        elif c.label == 'Expr':
            blk = self.Expr(c, result, blk)
        elif c.label == 'Call':
            blk = self.Call(c, result, blk)
        else:
            raise Exception, 'Unexpected Node %s' % str(c)

        return blk

    def CmpOp(self, node, result, blk):
        ops = {'==':il.EQ, '=!':il.NE, '<':il.LT, '<=':il.LE, '>':il.GT, '>=':il.GE}
        Ar = Symbol('r'+self.tmp(), il.Int())
        Br = Symbol('r'+self.tmp(), il.Int())
        blk = self.Expr(node.children[0], Ar, blk)
        blk = self.Expr(node.children[1], Br, blk)
        blk.insts += [
            il.Inst(ops[node.label],
            Ar,
            Br,
            result)
        ]
        return blk

    def Op(self, node, result, blk):
        ops = {'/':'DIV', '*':'MUL', '-':'SUB', '+':'ADD'}
        Ar = Symbol('r'+self.tmp(), il.Int())
        Br = Symbol('r'+self.tmp(), il.Int())
        blk = self.Expr(node.children[0], Ar, blk)
        blk = self.Expr(node.children[1], Br, blk)
        blk.insts +=  [
            il.Inst(il.ops[ops[node.label]],
            Ar,
            Br,
            result)
        ]
        return blk

    def Call(self, node, result, blk):
        assert node.label == 'Call'
        fun = self.objs[node.children[0]]
        #print self.objs, fun, node.children[0], self.objs['f']
        if isinstance(fun.type, il.Int):
            fun.type = fun.type.cast(il.FuncPointer)
        #print fun
        #print repr(fun)
        if len(node.children) != 1:
            blk = self.Params(node.children[1], blk)
        blk.insts += [ il.Inst(il.CALL, fun, 0, 0) ]
        blk.insts += [ il.Inst(il.RPRM, 0, 0, result)]
        return blk

    def Params(self, node, blk):
        assert node.label == 'Params'
        params = list()
        for c in node.children:
            result = Symbol('r'+self.tmp(), il.Int())
            blk = self.Expr(c, result, blk)
            params.append(result)
        params.reverse()
        for i, p in enumerate(params):
            blk.insts += [ il.Inst(il.IPRM, len(params)-1-i, p, 0) ]
        return blk

    def Int(self, node, result, blk):
        blk.insts += [ il.Inst(il.IMM, node, 0, result) ]
        return blk


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

