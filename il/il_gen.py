#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

from frontend.sl_parser import Parser, Lexer
from table import SymbolTable
import il

def print_blks(blks):
    print 'Basic Blocks:'
    blks = sorted(blks, key=lambda x: int(x.name[1:]))

    for blk in blks:
        print ' '*2, "block:", blk.name
        for i, inst in enumerate(blk.insts):
            print ' '*4, '(%i)' % i, inst
        print ' '*4, 'next ->', blk.next
        print ' '*4, 'prev ->', blk.prev
        print
    print

class generate(object):

    def __new__(cls, root, debug=False):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        self.debug = debug

        self.push_func('main')
        self.cfunc.scope_depth = 1
        entry = self.block()
        blk = self.Stmts(root, entry)
        main = self.pop_func()
        main.entry = entry
        main.exit = blk

        if debug:
            print_blks(self.blocks.values())

            print "Functions:"

            for name, f in sorted(self.functions.iteritems(), key=lambda x: x[0]):
                print f
            print
            print

        return self.objs, self.blocks, self.functions

    def __init__(self):
        il.Symbol.IDC = 0
        il.Type.IDC = 0
        self.fcount = 0
        self.tcount = 0
        self.bcount = 0

        self.blocks = dict()

        self.functions = dict()
        self.fstack = list()

        self.objs = SymbolTable()

    def tmp(self):
        self.tcount += 1
        return 't%i' % self.tcount

    def block(self):
        self.bcount += 1
        name = 'b%i' % self.bcount
        blk = il.Block(name)
        self.blocks[name] = blk
        self.cfunc.blks.append(blk)
        return blk

    def push_func(self, name=None):
        self.fcount += 1
        if name is None: name = 'f%i' % self.fcount
        self.functions[name] = il.Function(name)
        self.fstack.append(self.functions[name])
        self.cfunc.scope_depth = self.objs.depth + 1

    def pop_func(self):
        return self.fstack.pop()

    @property
    def cfunc(self):
        return self.fstack[-1]

    def Stmts(self, node, blk):
        assert node.label == 'Stmts'
        for c in node.children:
            if c.label == 'Assign':
                self.PreAssign(c)
            elif c.label == 'Var':
                self.PreVar(c)
        for c in node.children:
            #print c.label
            if c.label == 'Assign':
                blk = self.Assign(c, blk)
            elif c.label == 'Var':
                blk = self.Var(c, blk)
            elif c.label == 'Call':
                blk = self.Call(c, None, blk)
            elif c.label == 'Print':
                blk = self.Print(c, blk)
            elif c.label == 'If':
                blk = self.If(c, blk)
            elif c.label == 'While':
                blk = self.While(c, blk)
            else:
                raise Exception, c.label
        return blk

    def If(self, node, blk):
        assert node.label == 'If'

        thenblk = self.block()
        finalblk = self.block()
        elseblk = None

        if len(node.children) == 3:
            elseblk = self.block()
            blk = self.BooleanExpr(node.children[0], blk, thenblk, elseblk)
        else:
            blk = self.BooleanExpr(node.children[0], blk, thenblk, finalblk)

        thenblk = self.Stmts(node.children[1], thenblk)
        thenblk.link(finalblk, il.UNCONDITIONAL)
        thenblk.insts += [ il.Inst(il.J, finalblk, 0, 0) ]

        if len(node.children) == 3:
            #blk.insts += [ il.Inst(il.J, elseblk, 0, 0) ] ## This line must go here. subtle bug
            elseblk = self.Stmts(node.children[2], elseblk)
            elseblk.link(finalblk, il.UNCONDITIONAL)
            elseblk.insts += [ il.Inst(il.J, finalblk, 0, 0) ]

        return finalblk

    def While(self, node, blk):
        assert node.label == 'While'

        whileblk = self.block()
        blk.link(whileblk, il.UNCONDITIONAL)
        blk.insts += [ il.Inst(il.J, whileblk, 0, 0) ]

        thenblk = self.block()
        elseblk = self.block()
        blk = self.BooleanExpr(node.children[0], whileblk, thenblk, elseblk)

        thenblk = self.Stmts(node.children[1], thenblk)
        thenblk.link(whileblk, il.UNCONDITIONAL)
        thenblk.insts += [ il.Inst(il.J, whileblk, 0, 0) ]

        return elseblk

    def Print(self, node, blk):
        assert node.label == 'Print'

        c = node.children[0]
        if c.label == 'Expr':
            result = il.Symbol('r'+self.tmp(), il.Int())
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
            s = il.Symbol(name, il.Func(None))
            if name in self.objs.myscope:
                self.objs.add(s)
            elif name in self.objs:
                raise TypeError, "Cannot assign a function to a non local var."
            else:
                raise TypeError, "Variable name %s not declared." % (name)

    def PreVar(self, node):
        assert node.label == 'Var'
        name = node.children[0]


        if len(node.children) == 2:
            c = node.children[1]
            if c.label == 'Func':
                s = il.Symbol(name, il.Func(None))
                if name in self.objs.myscope:
                    raise TypeError, "Name '%s' redeclared in same scope." % name
                self.objs.add(s)

    def Assign(self, node, blk):
        assert node.label == 'Assign'
        name = node.children[0]
        c = node.children[1]

        if name in self.objs:
            result = self.objs[name]
        else:
            print node
            raise TypeError, 'Use of name %s without prior declaration' % name

        if c.label == 'Expr':
            if isinstance(result.type, il.Null):
                result.type = il.Int()
            blk = self.Expr(c, result, blk, toplevel=True)
        elif c.label == 'Func':
            if isinstance(result.type, il.Null):
                result.type = il.Func(None)
            blk = self.Func(c, name, blk)
        else:
            raise Exception, c.label

        return blk

    def Var(self, node, blk):
        assert node.label == 'Var'
        name = node.children[0]

        if len(node.children) == 1:
            if name in self.objs.myscope:
                raise TypeError, "Name '%s' redeclared in same scope." % name
            self.objs.add(il.Symbol(name, il.Null()))
        else:
            c = node.children[1]

            if c.label == 'Expr':
                if name in self.objs.myscope:
                    raise TypeError, "Name '%s' redeclared in same scope." % name
                result = il.Symbol(name, il.Int())
                self.objs.add(result)
                blk = self.Expr(c, result, blk, toplevel=True)
            elif c.label == 'Func':
                blk = self.Func(c, name, blk)
            else:
                raise Exception, c.label

        return blk

    def Func(self, node, name, blk):
        assert node.label == 'Func'
        parent_blk = blk

        self.push_func()
        blk = self.block()
        self.cfunc.entry = blk
        self.objs[name].type.entry = self.cfunc.name

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
        self.cfunc.exit = blk
        self.objs = self.objs.pop()
        self.pop_func()

        return parent_blk

    def Return(self, node, blk):
        assert node.label == 'Return'
        if node.children:
            if node.children[0].label == 'Expr':
                result = il.Symbol('r'+self.tmp(), il.Int())
                blk = self.Expr(node.children[0], result, blk)
                blk.insts += [ il.Inst(il.OPRM, 0, result, 0) ]
                self.cfunc.oparam_count += 1
            else:
                raise Exception, 'Expected Expr got %s' % node.children[0].label
        blk.insts += [ il.Inst(il.RTRN, 0, 0, 0) ]
        return blk

    def DParams(self, node, blk):
        assert node.label == 'DParams'
        for i, c in enumerate(node.children):
            t = il.Symbol(c, il.Int())
            self.objs.add(t)
            self.cfunc.params.append(c)
            blk.insts += [ il.Inst(il.GPRM, i, 0, t) ]
        return blk

    def Expr(self, node, result, blk, toplevel=False):
        if node.label == 'Expr':
            c = node.children[0]
        else:
            c = node

        if c.label == 'INT':
            blk = self.Int(c.children[0], result, blk)
        elif c.label == '/' or c.label == '*' or c.label == '-' or c.label == '+':
            blk = self.Op(c, result, blk)
        elif c.label == 'NAME':
            ## If it this is a top level expression (eg. c = a) then
            ## this is a copy instruction. Otherwise, this is a reference
            ## instruction, (eg. c = a + 2)
            ## c = a
            ##   MV A, 0, C
            ## c = a + 2
            ##   IMM 2, 0, tmp
            ##   ADD a, tmp, c
            if toplevel:
                blk.insts += [
                    il.Inst(il.MV, self.objs[c.children[0]], 0, result)
                ]
            else:
                result.clone(self.objs[c.children[0]])
        elif c.label == 'Call':
            blk = self.Call(c, result, blk)
        else:
            raise Exception, 'Unexpected Node %s' % str(c)

        return blk

    def BooleanExpr(self, node, blk, thenblk, elseblk):
        assert node.label == 'BooleanExpr'
        c = node.children[0]
        return self.BooleanOp(c, blk, thenblk, elseblk)

    def BooleanOp(self, c, blk, thenblk, elseblk, negate=False):
        if c.label == 'BooleanExpr':
            return self.BooleanOp(c.children[0], blk, thenblk, elseblk, negate)
        elif c.label in ['==', '!=', '<', '<=', '>', '>=']:
            Ar = il.Symbol('r'+self.tmp(), il.Int())
            Br = il.Symbol('r'+self.tmp(), il.Int())
            blk = self.Expr(c.children[0], Ar, blk)
            blk = self.Expr(c.children[1], Br, blk)
            inst = self.CmpOp(c, negate)
            blk.insts += [
                il.Inst(inst, Ar, Br, thenblk),
                il.Inst(il.J, elseblk, 0, 0),
            ]
            blk.link(thenblk, il.TRUE)
            blk.link(elseblk, il.FALSE)
        elif c.label in ('Or', 'And'):
            ## the blk become the A expressions block
            ## we allocate a new blk for B, the previous block is blk
            a = c.children[0]
            b = c.children[1]
            ablk = blk
            bblk = self.block()
            op = c.label
            bresult = self.BooleanOp(b, bblk, thenblk, elseblk, negate)
            if negate:
                if op == 'Or': op = 'And'
                elif op == 'And': op = 'Or'
            if op == 'Or':
                aresult = self.BooleanOp(a, ablk, thenblk, bresult, negate)
            elif op == 'And':
                aresult = self.BooleanOp(a, ablk, bresult, elseblk, negate)
            blk = aresult
        elif c.label == 'Not':
            blk = self.BooleanOp(c.children[0], blk, thenblk, elseblk, not negate)
        else:
            raise Exception, 'Unexpected Node %s' % c.label

        return blk


    def CmpOp(self, node, negate=False):
        ops = {
            '==':il.IFEQ,
            '!=':il.IFNE,
            '<':il.IFLT,
            '<=':il.IFLE,
            '>':il.IFGT,
            '>=':il.IFGE
        }
        ops_ = {
            '==':il.IFNE,
            '!=':il.IFEQ,
            '<':il.IFGE,
            '<=':il.IFGT,
            '>':il.IFLE,
            '>=':il.IFLT
        }
        if negate:
            return ops_[node.label]
        else:
            return ops[node.label]

    def Op(self, node, result, blk):
        ops = {'/':'DIV', '*':'MUL', '-':'SUB', '+':'ADD'}
        Ar = il.Symbol('r'+self.tmp(), il.Int())
        Br = il.Symbol('r'+self.tmp(), il.Int())
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
        if result is not None: blk.insts += [ il.Inst(il.RPRM, 0, 0, result)]
        return blk

    def Params(self, node, blk):
        assert node.label == 'Params'
        params = list()
        for c in node.children:
            result = il.Symbol('r'+self.tmp(), il.Int())
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

