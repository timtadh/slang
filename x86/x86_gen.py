#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from collections import deque

from frontend.sl_parser import Parser, Lexer
from il.table import SymbolTable
import il
from il import il_gen
import x86 as x

class generate(object):

    def __new__(cls, table, blocks, functions):
        self = super(generate, cls).__new__(cls)
        self.__init__()
        self.blocks = blocks
        self.functions = functions
        self.bp_offset = 0
        self.floc = dict()
        self.code = list()

        self.code += self.InitCode()
        self.Func('main', main=True)
        self.code += self.ExitCode()

        for f in self.functions.itervalues():
            if f.name == 'main': continue
            self.Func(f.name)

        #print '\n'.join(self.code)

        #raise Exception
        return '\n'.join(self.code) + '\n'


    def InitCode(self):
        return [
            '.section .data',
            'printf_msg:',
            r'  .ascii "%d\n\0"',
            'printf_arg:',
            r'  .long 0',
            '',
            '.section .text',
            '.global _start',
            x.label('_start'),
            x.movl(x.esp, x.ebp),
            x.movl(x.ebp, '0(%ebp)'),
            #'.global main',
            #x86.label('main'),
        ]

    def ExitCode(self):
        return [
            x.push('$0'),
            x.call("exit"),
        ]

    def gather_syms(self, blks):
        syms = set()
        for b in blks:
            for i in b.insts:
                if isinstance(i.a, il.Symbol): syms.add(i.a)
                if isinstance(i.b, il.Symbol): syms.add(i.b)
                if isinstance(i.result, il.Symbol): syms.add(i.result)
        return syms

    def place_symbols(self, syms):
        i = 7
        for sym in syms:
            #print sym, sym.type
            if issubclass(sym.type.__class__, il.Int):
                #print 'is subclass int'
                sym.type.basereg = x.ebp # set the base reg to the frame pointer
                sym.type.offset = -4 * i # set the offset
                i += 1
            #if issubclass(sym.type.__class__, il.FuncPointer):
                #print 'is subclass int'
                #sym.type.basereg = 1 # set the base reg to the frame pointer
                #sym.type.offset = -1 * i # set the offset
                #i += 1
            #if issubclass(sym.type.__class__, il.Func):
                #self.funcs.append(sym)
        return i-1

    def Func(self, name, main=False):
        self.code += [
            x.label(name)
        ]

        #print '->', insts
        func = self.functions[name]
        self.floc[func.name] = len(self.code)
        #insts = self.blocks[func.entry.name].insts

        self.bp_offset = 3

        if not main:
            self.code += self.FramePush(len(func.params))
        syms = self.gather_syms(func.blks)
        #print syms
        fp_offset = self.place_symbols(syms)
        #print syms
        self.code += [
            x.subl(x.cint(fp_offset*4), x.esp)
            #(vm.IMM, 4, fp_offset, 'start func %s' % (name)),
            #(vm.ADD, 1, 4, 'fp offset add inst'),
        ]

        def block(insts):
            for i in insts:
                if i.op == il.PRNT:
                    self.code += self.Print(i)
                elif i.op == il.IMM:
                    self.code += self.Imm(i)
                elif i.op == il.GPRM:
                    self.code += self.Gprm(i)
                elif i.op == il.IPRM:
                    self.code += self.Iprm(i)
                elif i.op == il.OPRM:
                    if not main and func.oparam_count > 0:
                        self.code += self.FramePop(len(func.params))
                    if func.oparam_count == 0:
                        raise Exception, "expected no return paramters got at least 1."
                    self.code += self.Oprm(i)
                elif i.op == il.RPRM:
                    self.code += self.Rprm(i)
                elif i.op == il.CALL:
                    self.code += self.Call(i)
                elif i.op == il.RTRN:
                    if not main and func.oparam_count == 0:
                        self.code += self.FramePop(len(func.params))
                    self.code += self.Return(i)
                elif i.op == il.MV:
                    self.code += self.Mv(i)
                elif i.op in [il.ADD, il.SUB, il.MUL, il.DIV]:
                    self.code += self.Op(i)
                elif i.op in [il.EQ, il.NE, il.LT, il.LE, il.GT, il.GE]:
                    self.code += self.CmpOp(i)
                elif i.op == il.BEQZ:
                    self.code += self.Beqt(i)
                elif i.op == il.J:
                    self.code += self.J(i)
                elif i.op == il.NOP:
                    self.code += self.Nop(i)
                else:
                    raise Exception, il.opsr[i.op]
                #if i.label is not None:
                    #print code[l]
                    #code[l] = (code[l][0], code[l][1], code[l][2], i.label)
        block(self.blocks[func.entry.name].insts)
        for b in func.blks:
            if b.name == func.entry.name: continue
            if b.name == func.exit.name: continue
            self.floc[b.name] = len(self.code)
            self.code += [ (vm.NOP, 0, 0, 'start of block %s' % b.name) ]
            block(self.blocks[b.name].insts)
        if func.entry.name != func.exit.name:
            b = func.exit
            self.floc[b.name] = len(self.code)
            self.code += [ (vm.NOP, 0, 0, 'start of block %s' % b.name) ]
            block(self.blocks[b.name].insts)

    def Nop(self, i):
        code = [
            (vm.NOP, 0, 0)
        ]
        return code

    def Gprm(self, i):
        code = [
            x.movl(x.mem(x.ebp, -(1+i.a)*4), x.eax),
            x.movl(x.eax, x.loc(i.result.type)),
        ]
        return code

    def Oprm(self, i):
        print i
        code = [
            x.movl(x.mem(x.esp, i.b.type.offset), x.eax),
            x.movl(x.eax, x.mem(x.esp, -(1+i.a)*4)),
        ]
        return code

    def Iprm(self, i):
        if isinstance(i.b.type, il.Func):
            # this is a function param not a value
            code = [
                x.leal(i.b.type.entry, x.eax),
                x.movl(x.eax, x.mem(x.esp, -(2+i.a)*4)),
            ]
        else:
            code = [
                x.movl(x.loc(i.b.type), x.eax),
                x.movl(x.eax, x.mem(x.esp, -(2+i.a)*4)),
            ]
        return code

    def Rprm(self, i):
        print i
        code = [
            x.movl(x.mem(x.esp, -(2+i.a)*4), x.eax),
            x.movl(x.eax, x.loc(i.result.type)),
        ]
        #self.var[i.result] = self.bp_offset
        #self.bp_offset += 1
        return code

    def Call(self, i):
        if isinstance(i.a.type, il.Func):
            code = [
                x.call(i.a.type.entry),
            ]
        else:
            code = [
                x.call('*'+x.loc(i.a.type)),
            ]
        return code

    def Return(self, i):
        code = list()
        #if len(self.code) >= 90 and len(self.code) < 110:
            #code = [
                #(vm.IMM,  3, len(self.code), 'DEBUG'),
                #(vm.PRNT, 3, 0, 'DEBUG'),
                #(vm.PRNT, 2, 0, 'DEBUG'),
                #(vm.EXIT, 0, 0, 'DEBUG'),
            #]
        code += [
            x.addl(x.cint(4), x.esp),
            x.jmp('*'+x.mem(x.esp, -4)),
            #x.ret(),
        ]
        return code

    def FramePush(self, param_count):
        p = param_count
        code = [
            # 0(ebp) == return address
            x.movl(x.ebp, x.mem(x.esp, -(1+p)*4)), #     1
            x.movl(x.esp, x.ebp),
            x.movl(x.ebx, x.mem(x.ebp, -(2+p)*4)),  # 2
            x.movl(x.edi, x.mem(x.ebp, -(3+p)*4)),  # 3
            x.movl(x.esi, x.mem(x.ebp, -(4+p)*4)),  # 4
            x.movl(x.ecx, x.mem(x.ebp, -(5+p)*4)),  # 5
            x.movl(x.edx, x.mem(x.ebp, -(6+p)*4)),  # 6
        ]
        return code

    def FramePop(self, param_count):
        p = param_count
        code = [
            x.movl(x.mem(x.ebp, -(6+p)*4), x.edx),
            x.movl(x.mem(x.ebp, -(5+p)*4), x.ecx),
            x.movl(x.mem(x.ebp, -(4+p)*4), x.esi),
            x.movl(x.mem(x.ebp, -(3+p)*4), x.edi),
            x.movl(x.mem(x.ebp, -(2+p)*4), x.ebx),
            x.movl(x.ebp, x.esp),                # restore stack pointer
            x.movl(x.mem(x.esp, -(1+p)*4), x.ebp),   # restore base(frame) pointer
        ]
        return code

    def Beqt(self, i):
        #self.labels[i.b] = None
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
        #self.labels[i.a] = None
        code = [
            (vm.IMM, 4, i.a),
            (vm.J, 4, 0),
        ]
        return code

    def Imm(self, i):
        code = [
            x.movl(x.cint(i.a), x.loc(i.result.type)),
        ]
        return code

    def Mv(self, i):
        code = [
            (vm.IMM, 3, i.a.type.offset, 'start MV'),
            (vm.ADD, 3, i.a.type.basereg),
            (vm.LOAD, 3, 3),
            (vm.IMM, 4, i.result.type.offset),
            (vm.ADD, 4, i.result.type.basereg),
            (vm.SAVE, 4, 3, 'Save in MV'),
        ]
        return code

    def Op(self, i):
        ops = {il.ADD:x.addl, il.SUB:x.subl, il.MUL:x.imull}
        if i.op == il.DIV:
            code = [
                x.movl(x.cint(0), x.edx),
                x.movl(x.loc(i.a.type), x.eax),
                x.divl(x.loc(i.b.type)),
                x.movl(x.eax, x.loc(i.result.type)),
            ]
        else:
            code = [
                x.movl(x.loc(i.a.type), x.eax),
                ops[i.op](x.loc(i.b.type), x.eax),
                x.movl(x.eax, x.loc(i.result.type)),
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
            #x.movl(x.loc(i.a.type), x.eax),
            #x.pushl(x.eax),
            x.pushl(x.loc(i.a.type)),
            x.pushl('$printf_msg'),
            x.call("printf"),
            x.addl(x.cint(8), x.esp)
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

