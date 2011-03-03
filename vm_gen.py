#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from sl_parser import Parser, Lexer
from table import SymbolTable
import il_gen, il
import vm

## TODO: This module is broken by changes to IL

class generate(object):

    def __new__(cls, main, funcs):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        self.var = dict()
        self.bp_offset = 0
        ##self.main = main
        #self.funcs = funcs
        self.floc = dict()
        code = list()
        code += self.InitCode()
        code += self.Func(main, True)
        code += self.ExitCode()
        for k, f in funcs.iteritems():
            self.floc[k] = len(code)
            code += self.Func(f)
        def transform(i):
            if i[0] == vm.IMM and i[2] in self.floc:
                return (i[0], i[1], self.floc[i[2]])
            return i
        code = [transform(i) for i in code]
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

    def Func(self, insts, main=False):
        labels = insts[1]
        insts = insts[0]
        #print '->', insts
        self.bp_offset = 3
        code = list()
        if not main: code += self.FramePush()
        for i in insts:
            if i.op == il.PRNT:
                code += self.Print(i)
            elif i.op == il.IMM:
                code += self.Imm(i)
            elif i.op == il.GPRM:
                code += self.Gprm(i)
            elif i.op == il.IPRM:
                code += self.Iprm(i)
            elif i.op == il.OPRM:
                code += self.Oprm(i)
            elif i.op == il.RPRM:
                code += self.Rprm(i)
            elif i.op == il.CALL:
                code += self.Call(i)
            elif i.op == il.RTRN:
                code += self.Return(i)
            elif i.op in [il.ADD, il.SUB, il.MUL, il.DIV]:
                code += self.Op(i)
            elif i.op in [il.EQ, il.NE, il.LT, il.LE, il.GT, il.GE]:
                code += self.CmpOp(i)
            else:
                raise Exception, il.opsr[i.op]
        return code

    def Gprm(self, i):
        code = [
            (vm.IMM,  3, 0, 'start GPRM'),
            (vm.ADD,  3, 0),
            (vm.IMM,  4, i.a+1),
            (vm.SUB,  3, 4),
            (vm.LOAD, 4, 3),
            (vm.IMM,  3, self.bp_offset),
            (vm.ADD,  3, 0),
            (vm.SAVE, 3, 4),
            (vm.IMM, 4, 1),
            (vm.ADD, 1, 4, 'end GPRM'),
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        #print code
        return code

    def Oprm(self, i):
        code = self.FramePop()
        code += [
            (vm.IMM,  4, i.a),            # offset for frame pointer (for saving)
            (vm.IMM,  3, self.var[i.b], 'Return Value offset'),  # offset for bp for loading return val
            (vm.ADD,  3, 1),              # $3 = offset($3) + $fp (which was the old bp)
            (vm.LOAD, 3, 3, 'Loading Return Value into $3'),              # $3 = *$3
            (vm.ADD,  4, 1),              # $4 = $4 + $fp
            (vm.SAVE, 4, 3),              # *$4 = $3
        ]
        return code

    def Iprm(self, i):
        if i.b[0] == 'f':
            # this is a function param not a value
            code = [
                (vm.IMM,  3, i.b, 'start put func as arg'),  # offset for bp for loading param val
                (vm.SAVE, 1, 3),              # *$fp = $3
                (vm.IMM,  4, 1),              # $4 = 1
                (vm.ADD,  1, 4, 'end put func as arg'),              # $fp += $4
            ]
        else:
            code = [
                (vm.IMM,  3, self.var[i.b]),  # offset for bp for loading param val
                (vm.ADD,  3, 0),              # $3 = offset($3) + $bp
                (vm.LOAD, 3, 3),              # $3 = *$3
                (vm.SAVE, 1, 3),              # *$fp = $3
                (vm.IMM,  4, 1),              # $4 = 1
                (vm.ADD,  1, 4),              # $fp += $4
            ]
        return code

    def Rprm(self, i):
        code = [
            (vm.IMM,  4, 0, 'Start RPRM'),              # $4 = 0
            (vm.ADD,  4, 1),              # $4 = $fp
            (vm.LOAD, 4, 4),              # $4 = *$4
            (vm.IMM,  3, self.bp_offset),
            (vm.ADD,  3, 0),
            (vm.SAVE, 3, 4),              # *$3 = $4
            (vm.IMM,  1, 1),              # $fp = 1
            (vm.ADD,  1, 3, 'End RPRM'),              # $fp += $3
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        return code

    def Call(self, i):
        if i.a[0] == 'f':
            code = [
                (vm.IMM,  3, i.a, 'start label function call'),  # load target address (this is a stub for now)
                (vm.PC,   2, 0),    # save the return program counter
                (vm.J,    3, 0, 'func call'),    # Jump to the function
            ]
        else:
            code = [
                (vm.IMM,  3, self.var[i.a], 'Start stack function call'),  # load target address (this is the actual address)
                (vm.ADD,  3, 0),
                (vm.LOAD, 3, 3),
                (vm.PC,   2, 0),    # save the return program counter
                (vm.J,    3, 0, 'func call'),    # Jump to the function
            ]
        return code

    def Return(self, i):
        code = [
            (vm.J, 2, 0),
        ]
        return code

    def FramePush(self):
        code = [
            (vm.IMM,  4, 0),  # START FUNC
            (vm.ADD,  4, 1),  # mv fp into reg[4]
            (vm.SAVE, 4, 0),  # stack save: save bp
            (vm.IMM,  3, 1),  # $3 = 1
            (vm.ADD,  4, 3),  # $4 += 1
            (vm.SAVE, 4, 1),  # stack save: save fp
            (vm.ADD,  4, 3),  # $4 += 1
            (vm.SAVE, 4, 2),  # stack save: save ra
            (vm.ADD,  4, 3),  # $4 += 1
            (vm.IMM,  0, 0),  # $bp = 0
            (vm.ADD,  0, 1),  # $bp = $fp
            (vm.IMM,  1, 0),  # $fp = 0
            (vm.ADD,  1, 4),  # $fp = $4
        ]
        return code

    def FramePop(self):
        code = [
            (vm.IMM, 4, 0),
            (vm.ADD, 4, 0),  # load bp into 4
            (vm.LOAD, 0, 4), # stack restore: bp
            (vm.IMM, 3, 1),  # $3 = 1
            (vm.ADD, 4, 3,), # $4 += 1
            (vm.LOAD, 1, 4), # stack restore: fp
            (vm.ADD, 4, 3,), # $4 += 1
            (vm.IMM, 3, 0),
            (vm.ADD, 3, 2),
            (vm.LOAD, 2, 4), # stack restore: ra
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
            (vm.IMM, 4, 1),
            (vm.ADD, 1, 4),
        ]
        self.var[i.result] = self.bp_offset
        self.bp_offset += 1
        return code

    def CmpOp(self, i):
        ops = {il.LT:vm.LT}
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
            (vm.IMM, 4, 1),
            (vm.ADD, 1, 4),
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
        return code

if __name__ == '__main__':

    code = generate(
        *il_gen.generate(
            Parser().parse('''
                _add = func(a, b) {
                    reflect = func(x) {
                        print x
                        y = x + 5
                        return y - 5
                    }
                    return reflect(a) + reflect(b)
                }
                add = func(f, a, b) {
                    return f(a, b)
                }
                print add(_add, 18, 37)
            ''', lexer=Lexer())
        )
    )
    #print code
    vm.run(code)

