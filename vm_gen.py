#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from collections import deque

from sl_parser import Parser, Lexer
from table import Symbol, SymbolTable
import il_gen, il
import vm

class generate(object):

    def __new__(cls, main, mlabels):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        #self.var = dict()
        self.bp_offset = 0
        ##self.main = main
        self.funcs = deque()
        self.floc = dict()
        self.labels = dict()
        code = list()
        code += self.InitCode()
        code += self.Func(main, mlabels, 'main', main=True)
        code += self.ExitCode()
        print self.funcs
        while self.funcs:
            fun = self.funcs.popleft()
            self.floc[fun.id] = len(code)
            code += self.Func(fun.type.code, fun.type.labels, fun.id)
        for c, i in enumerate(code):
            if len(i) > 3 and i[3] in self.labels:
                self.labels[i[3]] = c
        #print self.labels
        def transform(i):
            if isinstance(i[2], Symbol) and i[2].id in self.floc:
                return (i[0], i[1], self.floc[i[2].id])
            if i[0] == vm.IMM and i[2] in self.labels:
                return (i[0], i[1], self.labels[i[2]])
            return i
        code = [transform(i) for i in code]
        for c, i in enumerate(code):
            print '%3d : %-5s %s' % (c, vm.opsr[i[0]], str(i[1:])[1:-1].replace(',', ''))
        #raise Exception
        return code

    def InitCode(self):
        return [
            (vm.IMM, 4, 0, 'start init code'),
            (vm.IMM, 3, 0),
            (vm.SAVE, 3, 4),
            (vm.IMM, 3, 1),
            (vm.SAVE, 3, 4),
            (vm.IMM, 3, 2),
            (vm.SAVE, 3, 4),
            (vm.IMM, 1, 3),
            (vm.IMM, 0, 0),
            (vm.IMM, 2, 0, 'end init code'),
        ]

    def ExitCode(self):
        return [
            (vm.EXIT, 0,0)
        ]

    def gather_syms(self, insts):
        syms = set()
        for i in insts:
            if isinstance(i.a, Symbol): syms.add(i.a)
            if isinstance(i.b, Symbol): syms.add(i.b)
            if isinstance(i.result, Symbol): syms.add(i.result)
        return syms

    def place_symbols(self, syms):
        i = 1
        for sym in syms:
            #print sym, sym.type
            if issubclass(sym.type.__class__, il.Int):
                #print 'is subclass int'
                sym.type.basereg = 1 # set the base reg to the frame pointer
                sym.type.offset = -1 * i # set the offset
                i += 1
            if issubclass(sym.type.__class__, il.Func):
                self.funcs.append(sym)
        return i-1

    def Func(self, insts, labels, name, main=False):
        #print '->', insts
        self.bp_offset = 3
        code = list()
        if not main: code += self.FramePush()
        syms = self.gather_syms(insts)
        #print syms
        fp_offset = self.place_symbols(syms)
        #print syms
        code += [
            (vm.IMM, 4, fp_offset, 'start func %s' % (name)),
            (vm.ADD, 1, 4, 'fp offset add inst'),
        ]
        for i in insts:
            l = len(code)
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
            elif i.op == il.BEQZ:
                code += self.Beqt(i)
            elif i.op == il.J:
                code += self.J(i)
            elif i.op == il.NOP:
                code += self.Nop(i)
            else:
                raise Exception, il.opsr[i.op]
            if i.label is not None:
                print code[l]
                code[l] = (code[l][0], code[l][1], code[l][2], i.label)
        return code

    def Nop(self, i):
        code = [
            (vm.NOP, 0, 0)
        ]
        return code

    def Gprm(self, i):
        code = [
            (vm.IMM,  3, 0, 'start GPRM'),
            (vm.ADD,  3, 0),
            (vm.IMM,  4, i.a+1),
            (vm.SUB,  3, 4),
            (vm.LOAD, 4, 3),
            (vm.IMM,  3, i.result.type.offset),
            (vm.ADD,  3, i.result.type.basereg),
            (vm.SAVE, 3, 4, 'save in GPRM'),
            #(vm.IMM, 4, 1),
            #(vm.ADD, 1, 4, 'end GPRM'),
        ]
        #self.var[i.result] = self.bp_offset
        #self.bp_offset += 1
        #print code
        return code

    def Oprm(self, i):
        code = self.FramePop()
        code += [
            (vm.IMM,  4, i.b.type.offset, 'Return Value offset'),  # offset for bp for loading return val
            (vm.ADD,  3, 4),              # $3 = offset($3) + $fp (which was the old bp)
            (vm.LOAD, 3, 3, 'Loading Return Value into $3'),              # $3 = *$3
            (vm.IMM,  4, i.a),            # offset for frame pointer (for saving)
            (vm.ADD,  4, 1),              # $4 = $4 + $fp
            (vm.SAVE, 4, 3, 'end Oprm'),              # *$4 = $3
        ]
        return code

    def Iprm(self, i):
        if isinstance(i.b.type, il.Func):
            # this is a function param not a value
            code = [
                (vm.IMM,  3, i.b, 'start put func as arg'),  # offset for bp for loading param val
                (vm.SAVE, 1, 3, 'save in Iprm 1'),              # *$fp = $3
                (vm.IMM,  4, 1),              # $4 = 1
                (vm.ADD,  1, 4, 'end put func as arg'),              # $fp += $4
            ]
        else:
            code = [
                (vm.IMM,  3, i.b.type.offset),  # offset for bp for loading param val
                (vm.ADD,  3, i.b.type.basereg), # $3 = offset($3) + $bp
                (vm.LOAD, 3, 3),                # $3 = *$3
                (vm.SAVE, 1, 3, 'save in Iprm 2'),              # *$fp = $3
                (vm.IMM,  4, 1),              # $4 = 1
                (vm.ADD,  1, 4),              # $fp += $4
            ]
        return code

    def Rprm(self, i):
        print i
        code = [
            (vm.IMM,  4, 0, 'Start RPRM'),              # $4 = 0
            (vm.ADD,  4, 1),              # $4 = $fp
            (vm.LOAD, 4, 4),              # $4 = *$4
            (vm.IMM,  3, i.result.type.offset),
            (vm.ADD,  3, i.result.type.basereg),
            (vm.SAVE, 3, 4, 'save in Rprm'),              # *$3 = $4
            #(vm.IMM,  1, 0),              # $fp = 0
            #(vm.ADD,  1, 3, 'End RPRM'),              # $fp += $3
        ]
        #self.var[i.result] = self.bp_offset
        #self.bp_offset += 1
        return code

    def Call(self, i):
        if isinstance(i.a.type, il.Func):
            code = [
                (vm.IMM,  3, i.a, 'start label function call'),  # load target address (this is a stub for now)
                (vm.PC,   2, 0),    # save the return program counter
                (vm.J,    3, 0, 'func call'),    # Jump to the function
            ]
        else:
            code = [
                (vm.IMM,  3, i.a.type.offset, 'Start stack function call'),  # load target address
                (vm.ADD,  3, i.a.type.basereg),
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
            (vm.IMM,  4, 0, 'start frame push'),  # START FUNC
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
            (vm.ADD,  1, 4, 'end frame push'),  # $fp = $4
        ]
        return code

    def FramePop(self):
        code = [
            (vm.IMM, 4, 0, 'start frame pop'),
            (vm.ADD, 4, 0),  # load bp into 4
            (vm.LOAD, 0, 4), # stack restore: bp
            (vm.IMM, 3, 1),  # $3 = 1
            (vm.ADD, 4, 3,), # $4 += 1
            (vm.ADD, 4, 3,), # $4 += 1
            (vm.LOAD, 2, 4), # stack restore: ra
            (vm.SUB, 4, 3,), # $4 -= 1
            (vm.IMM, 3, 0),
            (vm.ADD, 3, 1),
            (vm.LOAD, 1, 4, 'end frame pop'), # stack restore: fp
        ]
        return code

    def Beqt(self, i):
        self.labels[i.b] = None
        code = [
            (vm.IMM, 3, i.a.type.offset, 'start beqt'),
            (vm.ADD, 3, i.a.type.basereg),
            (vm.LOAD, 3, 3),
            (vm.IMM, 4, i.b),
            (vm.BEQT, 3, 4, 'end beqt'),
        ]
        #for i in code:
            #print i
        return code

    def J(self, i):
        self.labels[i.a] = None
        code = [
            (vm.IMM, 4, i.a),
            (vm.J, 4, 0),
        ]
        return code

    def Imm(self, i):
        code = [
            (vm.IMM, 3, i.result.type.offset),
            (vm.ADD, 3, i.result.type.basereg),
            (vm.IMM, 4, i.a),
            (vm.SAVE, 3, 4, 'Save in IMM'),
        ]
        #self.var[i.result] = self.bp_offset
        #self.bp_offset += 1
        return code

    def Op(self, i):
        ops = {il.ADD:vm.ADD, il.SUB:vm.SUB, il.MUL:vm.MUL, il.DIV:vm.DIV}
        code = [
            (vm.IMM, 3, i.b.type.offset),
            (vm.ADD, 3, i.b.type.basereg),
            (vm.LOAD, 3, 3),
            (vm.IMM, 4, i.a.type.offset),
            (vm.ADD, 4, i.a.type.basereg),
            (vm.LOAD, 4, 4),
            (ops[i.op], 4, 3),
            (vm.IMM, 3, i.result.type.offset),
            (vm.ADD, 3, i.result.type.basereg),
            (vm.SAVE, 3, 4, 'Save in Op'),
        ]
        return code

    def CmpOp(self, i):
        ops = {il.EQ:vm.EQ, il.NE:vm.NE, il.LT:vm.LT, il.LE:vm.LE,
               il.GT:vm.GT, il.GE:vm.GE}
        code = [
            (vm.IMM, 3, i.b.type.offset, 'start comparison'),
            (vm.ADD, 3, i.b.type.basereg),
            (vm.LOAD, 3, 3),
            (vm.IMM, 4, i.a.type.offset),
            (vm.ADD, 4, i.a.type.basereg),
            (vm.LOAD, 4, 4),
            (ops[i.op], 4, 3),
            (vm.IMM, 3, i.result.type.offset),
            (vm.ADD, 3, i.result.type.basereg),
            (vm.SAVE, 3, 4, 'end comparison'),
        ]
        return code

    def Print(self, i):
        print i
        code = [
            (vm.IMM, 3, i.a.type.offset),
            (vm.ADD, 3, i.a.type.basereg),
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

