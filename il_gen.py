#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
from table import SymbolTable
import il

prebuilt_funcs = {
    'print':il.Func([{'type':il.Int(), 'name':None}], []),
    '__add':il.Func(
        [{'type':il.Int(), 'name':None}, {'type':il.Int(), 'name':None}],
        [{'type':il.Int(), 'name':None}]
    ),
    'exit':il.Func([], [])
}

class generate(object):

    def __new__(cls, root):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        r = self.Arith(root)
        r += [ il.Inst(il.PRNT, r[-1].result, 0, 0)]
        #print '---'
        #parents = list()
        #for x,y in self.functions.iteritems():
            #print x
            #print ' '*4, 'symbols'
            #parents.append(y['symbols'].parent)
            #for a,b in y['symbols'].iteritems():
                #print ' '*8, a, b
            #print ' '*4, 'code', y['code']
        #for x in parents:
            #print repr(x)
        #print '---'
        #for x,y in self.objs.iteritems():
            #print x, y
        #print '---'
        print r
        return r

    def __init__(self):
        self.functions = dict()
        self.fcount = 0
        self.tcount = 0
        self.objs = SymbolTable(prebuilt_funcs)

    def tmp(self):
        self.tcount += 1
        return 't%i' % self.tcount

    def Arith(self, node):
        if node.label == 'Arith':
            c = node.children[0]
        else:
            c = node
        if c.label == 'INT':
            return self.Int(c.children[0])
        elif c.label == '/' or c.label == '*' or c.label == '-' or c.label == '+':
            return self.Op(c)
        else:
            raise Exception, 'Unexpected Node %s' % str(c)

    def Op(self, node):
        ops = {'/':'DIV', '*':'MUL', '-':'SUB', '+':'ADD'}
        A = self.Arith(node.children[0])
        B = self.Arith(node.children[1])
        return A + B + [
            il.Inst(il.ops[ops[node.label]],
            A[-1].result,
            B[-1].result,
            self.tmp())
        ]

    def Int(self, node):
        return [ il.Inst(il.IMM, node, 0, self.tmp()) ]


    # ------------------------------------------------------------------------ #


if __name__ == '__main__':

    print il.run(generate(Parser().parse(''' 2*3/(4-5*(12*32-15)) ''', lexer=Lexer())))
    print il.run(generate(Parser().parse(''' 2 ''', lexer=Lexer())))
