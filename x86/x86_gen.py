#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


from collections import deque

from frontend.sl_parser import Parser, Lexer
from il.table import SymbolTable
import il, cf, df
from il import il_gen
import x86 as x

class generate(object):
    '''Generates 32bit x86 assembly for `as` from the output of the Parser. Acts
    like a function even though it is a declared as a class.'''

    def __new__(cls, table, blocks, functions):
        '''Generates x86 asm.
        @param table : The symbol table.
        @param blocks : The basic blocks.
        @param functions : The functions.
        @returns : A string, the x86 assembly. Suitable for input into `as`
        '''
        self = super(generate, cls).__new__(cls)
        self.table = table
        self.blocks = blocks
        self.functions = functions
        cf.analyze(table, blocks, functions)
        df.analyze(df.livevar.LiveVariable, functions, False, True)
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
        return '\n'.join(str(line) for line in self.code) + '\n'

    def __init__(self):
        '''Initializes state instance variables.'''
        self.code = list()
        self.cfunc = None

    def emit(self, inst, src, targ=None):
        '''emit the specified instruction with src as source operand and targ
            as the target operand. Handles requesting the operands from a
            non-local stack frame as necessary.

            using ebx or ecx is not allowed for either the src or targ.
        '''

        ## We have several choices to make in order to emit the right inst.
        ## (1) does the inst only refer to symbols local to the current scope?
        ##      (a) if yes: emit the instruction with no changes
        ##      (b) if no: detirmine what changes have to be made.
        ## (2) We now know the instruction is not local. One (but not both) of
        ##     the symbols does not come from this stack frame. That means they
        ##     have to be fetched from the appropriate stack frame. We detirmine
        ##     the appropriate frame to fetch (or put) the sym from(to) by
        ##     consulting the display.
        ## (3) The display is a static array:
        ##
        ##               +------------+------------+------------+------------+
        ##   scope depth | 0          | 1          | 2          | 3          |
        ##               +------------+------------+------------+------------+
        ## frame address | 0x???????? | 0x???????? | 0x???????? | 0x???????? |
        ##               +------------+------------+------------+------------+
        ##
        ##     The 'frame address' contains the address of the the stack frame
        ##     most recently seen function. When that function returns it will
        ##     update the display with the previous address it contained. When
        ##     A new function is called at that scope depth a new address will
        ##     be placed in the display and the old will be saved.
        ##
        ## (4) Therefore to get the non-local symbols we simply need to consult
        ##     the display to find the appropriate frame. Each symbol knows what
        ##     scope-depth it was declared at.
        ##
        ## NB: The symbols store there scope depths starting at 1. Therefore, in
        ##     order to index into the display one must subtract 1 from the
        ##     stored scope depth.
        ##
        ## NB: We multiply by 4 because each address is 4 bytes wide.


        if isinstance(src, il.Symbol) and isinstance(targ, il.Symbol):
            raise Exception, (
                'Cannot emit an instruction with both source and target as '
                'symbols'
            )
        elif isinstance(src, il.Symbol) and targ is None:
            if src.islocal(self.cfunc):
                return [ inst(x.loc(src.type)) ]
            return [
                x.movl(x.cint(4*(src.scope_depth-1)), x.ebx), # compute the
                                                              # index into the
                                                              # display and
                                                              # store in ebx

                x.movl(x.static('display', x.ebx), x.ebx),    # get the non-
                                                              # local stack
                                                              # pointer and
                                                              # store in ebx

                inst(x.mem(x.ebx, src.type.offset)),          # emit the inst.
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
                ## This version is slightly tricky we have to fetch and store
                ## the contents of the variable stored in the non-local stack
                ## frame.
                x.movl(x.cint(4*(targ.scope_depth-1)), x.ebx),
                x.movl(x.static('display', x.ebx), x.ebx),
                x.movl(x.mem(x.ebx, targ.type.offset), x.ecx),
                inst(src, x.ecx),
                x.movl(x.ecx, x.mem(x.ebx, targ.type.offset)),
            ]
        else:
            return [ inst(src, targ) ]

    def InitCode(self):
        '''The pre-amble to the generated code. Contains data and the _start
        label. Creates a new stack frame.'''
        return [
            '.section .data',
            'printf_msg:',
            r'  .ascii "%d\n\0"',

            ## START DEBUG MESSAGES ##
            'push_msg:',
            r'  .ascii "push 0x%x\n\0"',
            'pop1_msg:',
            r'  .ascii "pop1 0x%x\n\0"',
            'pop2_msg:',
            r'  .ascii "pop2 0x%x\n\0"',
            ## END DEBUG MESSAGES ##

            ## The display stores the location of non-local stack frames
            ## see. def emit(...)
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
        '''Exits the program and returns to the OS. Currently implemented by
        calling into the libc exit function. In the past it directly generated
        the syscall.'''
        return [
            x.push('$0'),
            x.call("exit"),
        ]

    def gather_syms(self, blks):
        '''Gather the symbols used through out the function.
        @param blks: The blks that make up the function under consideration.
        @returns : the symbols as a set()'''
        syms = set()
        for b in blks:
            for i in b.insts:
                if isinstance(i.a, il.Symbol): syms.add(i.a)
                if isinstance(i.b, il.Symbol): syms.add(i.b)
                if isinstance(i.result, il.Symbol): syms.add(i.result)
        return syms

    def place_symbols(self, syms, func):
        '''Determines the location of the symbols in the stack frame for the
        function. Eg. it sets sym.type.basereg and sym.type.offset for each
        symbol.
        @param syms : the set of symbols (generated by gather_syms)
        @param func : the current function (need to place params).
        @returns : The size of the stack frame in machine words.'''

        ## 8 is a constant, depicting the number of registers we (the callee)
        ## are storing for the caller. This should probably be refactored. It
        ## is a magic number right now.
        i = 8 + len(func.params)
        for sym in syms:
            ## We only need to place symbols that are sub-classes of integers.
            ## Why? Because the only other type we current have are Functions,
            ## functions do not need to be placed in the stack frame. Function
            ## pointers are sub-classes of integers so they are handled by this
            ## code.
            if issubclass(sym.type.__class__, il.Int) and sym.islocal(func):
                sym.type.basereg = x.ebp # set the base reg to the frame pointer
                sym.type.offset = -4 * i # set the offset (since we index from
                                         # the frame (base) pointer we need to
                                         # subtract (not add) therefore the
                                         # offset is negative.
                i += 1
        return i-1

    def Func(self, name, main=False):
        '''Generates x86 code for the function given by name. This is the entry
        point for all code generation.'''

        ## Get the function.
        func = self.functions[name]
        self.cfunc = func

        ## Generate a label for the function
        self.code += [
            x.label(name)
        ]

        ## If this is not the `main` function generate a stack push
        if not main:
            self.code += self.FramePush(len(func.params), func.scope_depth)

        ## Move the stack pointer down. This creates the stack frame.
        syms = self.gather_syms(func.blks)
        sp_offset = self.place_symbols(syms, func)
        self.code += [
            x.subl(x.cint(sp_offset*4), x.esp)
        ]

        def block(insts):
            '''Generate the x86 instruction for the given block of instructions.
            '''

            ## We could do something more clever than switch case here, but I
            ## (for now) perfer the simplicity.
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
                    ## OPRMs always appear directly before RTRN instructions.
                    ## Based on the way the stack frame pop is generated the pop
                    ## must be generated before the OPRM instruction. So the
                    ## output params can be properly returned.
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

        ## generate a label for the entry block of the function.
        self.code += [ x.label(func.entry.name) ]
        block(self.blocks[func.entry.name].insts) # generate the function.

        ## for each block in the function (excluding entry and exit) generate
        ## the code.
        for b in func.blks:
            if b.name == func.entry.name: continue
            if b.name == func.exit.name: continue
            self.code += [ x.label(b.name) ]
            self.code += [ x.nop() ]
            block(self.blocks[b.name].insts)

        ## If there a distinct exit block, generate it.
        if func.entry.name != func.exit.name:
            self.code += [ x.label(func.exit.name) ]
            b = func.exit
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
        code = [
            x.movl(x.mem(x.esp, -(2+i.a)*4), x.eax),
            x.movl(x.eax, x.loc(i.result.type)),
        ]
        return code

    def Call(self, i):
        if isinstance(i.a.type, il.Func):
            code = [
                x.call(i.a.type.entry),
            ]
        else:
            code = [
                x.call(x.loc(i.a.type, True)),
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
            x.jmp(x.mem(x.esp, -4, True)),
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

