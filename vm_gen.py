#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
from table import SymbolTable
import il_gen, il
import vm

class generate(object):

    def __new__(cls, main, funcs):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        self.var = dict()
        self.bp_offset = 0
        self.main = main
        self.funcs = funcs
        code = list()
        code += self.InitCode()
        code += self.Func(main)
        code += self.ExitCode()
        for k, f in funcs.iteritems():
            code += self.Func(f)
        return code

    def InitCode(self):
        return [
            (vm.IMM, 4, 0),
            (vm.IMM, 3, 0),
            (vm.SAVE, 3, 4),
            (vm.IMM, 3, 1),
            (vm.SAVE, 3, 4),
            (vm.IMM, 3, 2),
            (vm.SAVE, 3, 4),
            (vm.IMM, 1, 3),
            (vm.IMM, 0, 0),
            (vm.IMM, 2, 0),
        ]

    def ExitCode(self):
        return [
            (vm.EXIT, 0,0)
        ]

    def Func(self, insts):
        print '->', insts
        self.bp_offset = 3
        code = list()
        for i in insts:
            if i.op == il.PRNT:
                code += self.Print(i)
            elif i.op == il.IMM:
                code += self.Imm(i)
            elif i.op == il.GPRM:
                code += self.Gprm(i)
            elif i.op in [il.ADD, il.SUB, il.MUL, il.DIV]:
                code += self.Op(i)
            else:
                raise Exception, il.opsr[i.op]
        return code

    def Gprm(self, i):
        code = [
            (vm.IMM, 3, 0),
            (vm.ADD, 3, 0),
            (vm.IMM, 4, i.a+1),
            (vm.SUB, 3, 4),
            (vm.LOAD, 4, 3),
            (vm.IMM, 3, self.bp_offset),
            (vm.ADD, 3, 0),
            (vm.SAVE, 3, 4),
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        print code
        return code

    def Oprm(self, i):
        code = [
        ]
        return code


    ## TODO: Hand verify and prove correct FramePush
    def FramePush(self, i):
        code = [
            (IMM, 4, 0),  # START FUNC
            (ADD, 4, 1),  # mv fp into reg[4]
            (IMM, 3, 2),
            (ADD, 4, 3),  # reg[4] += 2
            (SAVE, 4, 0), # stack save: save bp
            (IMM, 3, 1),
            (ADD, 4, 3),  # reg[4] += 1
            (SAVE, 4, 1), # stack save: save fp
            (ADD, 4, 3),  # reg[4] += 1
            (SAVE, 4, 2), # stack save: save ra
            (ADD, 4, 3),  # reg[4] += 1
            (IMM, 0, 0),
            (ADD, 0, 1),  # mv fp to bp'
            (IMM, 1, 0),
            (ADD, 1, 4),  # mv $4 to fp
        ]

    ## TODO: Hand verify and prove correct FramePop
    def FramePop(self, i):
        # we need to do the frame pop before loading output Params
        # but the frame pop and output params loading must by nature be tightly
        # coupled.
        code = [
            (IMM, 4, 0),
            (ADD, 4, 0),  # load bp into 4
            (IMM, 3, 2),
            (ADD, 4, 3),  # reg[4] += 2
            (LOAD, 0, 4), # stack restore: bp
            (ADD, 4, 3,), # reg[4] += 2
            (LOAD, 2, 4), # stack restore: ra
            (IMM, 3, 1),
            (SUB, 4, 3),  # reg[4] -= 1
            #(IMM, 3, 0),
            #(ADD, 3, 1),  # mv the fp into register 3 (allowing us to put in the return)
            (LOAD, 1, 4), # stack restore: fp
        ]
        return code

    def Imm(self, i):
        code = [
            (vm.IMM, 3, self.bp_offset),
            (vm.ADD, 3, 0),
            (vm.IMM, 4, i.a),
            (vm.SAVE, 3, 4),
            (vm.IMM, 4, 1),
            (vm.ADD, 1, 4),
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        return code

    def Op(self, i):
        ops = {il.ADD:vm.ADD, il.SUB:vm.SUB, il.MUL:vm.MUL, il.DIV:vm.DIV}
        code = [
            (vm.IMM, 3, self.var[i.b]),
            (vm.ADD, 3, 0),
            (vm.LOAD, 3, 3),
            (vm.IMM, 4, self.var[i.a]),
            (vm.ADD, 4, 0),
            (vm.LOAD, 4, 4),
            (ops[i.op], 4, 3),
            (vm.IMM, 3, self.bp_offset),
            (vm.ADD, 3, 0),
            (vm.SAVE, 3, 4),
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        return code

    def Print(self, i):
        code = [
            (vm.IMM, 3, self.var[i.a]),
            (vm.ADD, 3, 0),
            (vm.LOAD, 4, 3),
            (vm.PRNT, 4, 0)
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        return code

if __name__ == '__main__':

    code = generate(
        *il_gen.generate(
            Parser().parse('''
                add = func(a,b) { return a + b}
                print add(2, 3)
            ''', lexer=Lexer())
        )
    )
    print code
    print vm.run(code)
