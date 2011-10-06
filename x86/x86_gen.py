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
        self.table = table
        self.blocks = blocks
        self.functions = functions
        self.__init__()

        #print 'max scope depth', table.max_depth

        self.code += self.InitCode()
        self.Func('main', main=True)
        self.code += self.ExitCode()



        for fname in sorted(self.functions.keys()):
            if fname == 'main': continue
            f = self.functions[fname]
            self.Func(f.name)

        #print '\n'.join(self.code)
        for line in self.code:
            print line

        #raise Exception
        return '\n'.join(self.code) + '\n'

    def __init__(self):
        self.bp_offset = 0
        self.floc = dict()
        self.code = list()
        self.cfunc = None

    def emit(self, inst, src, targ=None):
        '''emit the specified instruction with src as source operand and targ
            as the target operand. Handles requesting the operands from a non-local
            stack frame as necessary.

            using ebx or ecx is not allowed for either the src or targ.
        '''
        #print inst, src, targ
        if isinstance(src, il.Symbol) and isinstance(targ, il.Symbol):
            raise Exception, 'Cannot emit an instruction with both source and target as symbols'
        elif isinstance(src, il.Symbol) and targ is None:
            if src.islocal(self.cfunc):
                return [ inst(x.loc(src.type)) ]
            return [
                x.movl(x.cint(4*(src.scope_depth-1)), x.ebx),
                x.movl(x.static('display', x.ebx), x.ebx),
                inst(x.mem(x.ebx, src.type.offset)),
            ]
        elif not isinstance(src, il.Symbol) and targ is None:
            return [ inst(src), ]
        elif isinstance(src, il.Symbol) and targ is not None:
            if src.islocal(self.cfunc):
                return [ inst(x.loc(src.type), targ) ]
            return [
                x.movl(x.cint(4*(src.scope_depth-1)), x.ebx),
                x.movl(x.static('display', x.ebx), x.ebx),
                inst(x.mem(x.ebx, src.type.offset), targ),
            ]
        elif isinstance(targ, il.Symbol):
            #print inst, src, targ, targ.type.basereg
            if targ.islocal(self.cfunc):
                return [ inst(src, x.loc(targ.type)) ]
            return [
                x.movl(x.cint(4*(targ.scope_depth-1)), x.ebx),
                x.movl(x.static('display', x.ebx), x.ebx),
                x.movl(x.mem(x.ebx, targ.type.offset), x.ecx),
                inst(src, x.ecx),
                x.movl(x.ecx, x.mem(x.ebx, targ.type.offset)),
            ]
        else:
            return [ inst(src, targ) ]

    def InitCode(self):
        return [
            '.section .data',
            'printf_msg:',
            r'  .ascii "%d\n\0"',
            'push_msg:',
            r'  .ascii "push 0x%x\n\0"',
            'pop1_msg:',
            r'  .ascii "pop1 0x%x\n\0"',
            'pop2_msg:',
            r'  .ascii "pop2 0x%x\n\0"',
            'display:',
            r'  .long %s' % ', '.join('0' for x in xrange(self.table.max_depth)),
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

    def place_symbols(self, syms, func):
        i = 8 + len(func.params)
        for sym in syms:
            #print sym, sym.islocal(func), func.name
            if issubclass(sym.type.__class__, il.Int) and sym.islocal(func):
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
        #print name
        self.code += [
            x.label(name)
        ]

        #print '->', insts
        func = self.functions[name]
        self.cfunc = func
        #insts = self.blocks[func.entry.name].insts

        self.bp_offset = 3

        if not main:
            self.code += self.FramePush(len(func.params), func.scope_depth)
        syms = self.gather_syms(func.blks)
        #print syms
        fp_offset = self.place_symbols(syms, func)
        #print name, 'fp_offset', fp_offset
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
                        self.code += self.FramePop(len(func.params), func.scope_depth)
                    if func.oparam_count == 0:
                        raise Exception, "expected no return paramters got at least 1."
                    self.code += self.Oprm(i)
                elif i.op == il.RPRM:
                    self.code += self.Rprm(i)
                elif i.op == il.CALL:
                    self.code += self.Call(i)
                elif i.op == il.RTRN:
                    if not main and func.oparam_count == 0:
                        self.code += self.FramePop(len(func.params), func.scope_depth)
                    self.code += self.Return(i)
                elif i.op == il.MV:
                    self.code += self.Mv(i)
                elif i.op in [il.ADD, il.SUB, il.MUL, il.DIV]:
                    self.code += self.Op(i)
                elif i.op in [il.IFEQ, il.IFNE, il.IFLT, il.IFLE, il.IFGT, il.IFGE]:
                    self.code += self.BranchOp(i)
                elif i.op == il.J:
                    self.code += self.J(i)
                elif i.op == il.NOP:
                    self.code += self.Nop(i)
                else:
                    raise Exception, il.opsr[i.op]
                #if i.label is not None:
                    #print code[l]
                    #code[l] = (code[l][0], code[l][1], code[l][2], i.label)
        self.code += [ x.label(func.entry.name) ]
        block(self.blocks[func.entry.name].insts)
        for b in func.blks:
            if b.name == func.entry.name: continue
            if b.name == func.exit.name: continue
            self.code += [ x.label(b.name) ]
            self.floc[b.name] = len(self.code)
            self.code += [ x.nop() ]
            block(self.blocks[b.name].insts)
        if func.entry.name != func.exit.name:
            self.code += [ x.label(func.exit.name) ]
            b = func.exit
            self.floc[b.name] = len(self.code)
            self.code += [ x.nop() ]
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
        #print i
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
        #print i
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

    def FramePush(self, param_count, scope_depth):
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
            x.movl(x.cint(4*(scope_depth-1)), x.ebx),
            x.movl(x.static('display', x.ebx), x.eax),
            x.movl(x.eax, x.mem(x.ebp, -(7+p)*4)), #7


            #x.subl(x.cint(8*4), x.esp),
            #x.movl(x.cint(4*(scope_depth-1)), x.ebx),
            #x.pushl(x.static('display', x.ebx)),
            #x.pushl('$push_msg'),
            #x.call("printf"),
            #x.addl(x.cint(8*4 + 8), x.esp),


            x.movl(x.cint(4*(scope_depth-1)), x.ebx),
            x.movl(x.ebp, x.static('display', x.ebx)),
            '',

        ]
        return code

    def FramePop(self, param_count, scope_depth):
        p = param_count
        code = [
            '',
            #x.movl(x.cint(4*(scope_depth-1)), x.ebx),
            #x.pushl(x.static('display', x.ebx)),
            #x.pushl('$pop1_msg'),
            #x.call("printf"),
            #x.addl(x.cint(8), x.esp),

            x.movl(x.cint(4*(scope_depth-1)), x.ebx),
            x.movl(x.mem(x.ebp, -(7+p)*4), x.eax),
            x.movl(x.eax, x.static('display', x.ebx)),

            #x.movl(x.cint(4*(scope_depth-1)), x.ebx),
            #x.pushl(x.static('display', x.ebx)),
            #x.pushl('$pop2_msg'),
            #x.call("printf"),
            #x.addl(x.cint(8), x.esp),

            x.movl(x.mem(x.ebp, -(6+p)*4), x.edx),
            x.movl(x.mem(x.ebp, -(5+p)*4), x.ecx),
            x.movl(x.mem(x.ebp, -(4+p)*4), x.esi),
            x.movl(x.mem(x.ebp, -(3+p)*4), x.edi),
            x.movl(x.mem(x.ebp, -(2+p)*4), x.ebx),
            x.movl(x.ebp, x.esp),                # restore stack pointer
            x.movl(x.mem(x.esp, -(1+p)*4), x.ebp),   # restore base(frame) pointer
        ]
        return code

    def BranchOp(self, i):
        ops = {il.IFEQ:x.je, il.IFNE:x.jne, il.IFLT:x.jl, il.IFLE:x.jle,
               il.IFGT:x.jg, il.IFGE:x.jge}
        code = [
            x.movl(x.loc(i.a.type), x.eax),
            x.cmpl(x.loc(i.b.type), x.eax),
            ops[i.op](i.result.name)
        ]
        #for i in code:
            #print i
        return code

    def J(self, i):
        #self.labels[i.a] = None
        code = [
            x.jmp(i.a.name)
        ]
        return code

    def Imm(self, i):
        code = self.emit(x.movl, x.cint(i.a), i.result)
        return code

    def Mv(self, i):
        code = [
            x.movl(x.loc(i.a.type), x.eax),
            x.movl(x.eax, x.loc(i.result.type))
        ]
        return code

    def Op(self, i):
        #print i
        ops = {il.ADD:x.addl, il.SUB:x.subl, il.MUL:x.imull}
        code = []
        if i.op == il.DIV:
            code += [ x.movl(x.cint(0), x.edx), ]
            code += self.emit(x.movl, i.a, x.eax)
            code += self.emit(x.divl, i.b)
            code += self.emit(x.movl, x.eax, i.result)
        else:
            code += self.emit(x.movl, i.a, x.eax)
            code += self.emit(ops[i.op], i.b, x.eax)
            code += self.emit(x.movl, x.eax, i.result)
        return code

    def Print(self, i):
        code = self.emit(x.pushl, i.a)
        code += [
            x.pushl('$printf_msg'),
            x.call("printf"),
            x.addl(x.cint(8), x.esp),
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

