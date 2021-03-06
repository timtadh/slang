#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools, sys

opsr = (
    'LOAD', 'SAVE', 'IMM', 'J', 'PC', 'ADD', 'SUB', 'MUL', 'DIV', 'EXIT', 'PRNT',
    'BEQT', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE', 'AND', 'OR', 'NOT', 'NOP'
)
ops = dict((k, i) for i, k in enumerate(opsr))
sys.modules[__name__].__dict__.update(ops)

A = [J, PC]
B = [LOAD, IMM, ADD, SUB, MUL, DIV, PRNT, BEQT, EQ, NE, LT, LE, GT, GE, AND, OR, NOT]
C = [SAVE]

DEBUG = False

prints = list()

def load(regs, stack, pc, r1, r2):
    regs[r1] = stack[regs[r2]]
    return pc + 1
def save(regs, stack, pc, r1, r2):
    if DEBUG: print r1, '->', regs[r1]
    if DEBUG: print r2, '->', regs[r2]
    #print r1, r2, ':',  regs[r1], regs[r2]
    if DEBUG: print len(stack), len(stack) == regs[r2]
    if len(stack) == regs[r2]:
        stack.append(regs[r1])
        #print stack
    elif len(stack) < regs[r2]:
        while len(stack) < regs[r2]:
            stack.append(0)
        stack.append(regs[r1])
        #raise Exception, "Address out of range"
    else:
        stack[regs[r2]] = regs[r1]
    return pc + 1
def imm(regs, stack, pc, reg, immediate):
    regs[reg] = immediate
    return pc + 1
def j(regs, stack, pc, reg, addr):
    return regs[reg]
def pc(regs, stack, pc, reg, addr):
    regs[reg] = pc + 2
    return pc + 1
def add(regs, stack, pc, r1, r2):
    #print '->', regs[r1], regs[r2], regs[r1] + regs[r2]
    regs[r1] += regs[r2]
    return pc + 1
def sub(regs, stack, pc, r1, r2):
    regs[r1] -= regs[r2]
    return pc + 1
def mul(regs, stack, pc, r1, r2):
    regs[r1] *= regs[r2]
    return pc + 1
def div(regs, stack, pc, r1, r2):
    regs[r1] /= regs[r2]
    return pc + 1
def prin(regs, stack, pc, r1, r2):
    prints.append(regs[r1])
    return pc + 1
def beqt(regs, stack, pc, r1, r2):
    if regs[r1] == True:
        return regs[r2]
    return pc + 1
def eq(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] == regs[r2]
    return pc + 1
def ne(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] != regs[r2]
    return pc + 1
def lt(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] < regs[r2]
    return pc + 1
def le(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] <= regs[r2]
    return pc + 1
def gt(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] > regs[r2]
    return pc + 1
def ge(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] >= regs[r2]
    return pc + 1
def _and(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] and regs[r2]
    return pc + 1
def _or(regs, stack, pc, r1, r2):
    regs[r1] = regs[r1] or regs[r2]
    return pc + 1
def _not(regs, stack, pc, r1, r2):
    regs[r1] = not regs[r1]
    return pc + 1
def nop(regs, stack, pc, r1, r2):
    return pc + 1

INSTS = {
    LOAD:load, SAVE:save, IMM:imm, J:j, PC:pc, ADD:add, SUB:sub, MUL:mul,
    DIV:div, PRNT:prin, BEQT:beqt,
    EQ:eq, NE:ne, LT:lt, LE:le, GT:gt, GE: ge,
    AND:_and, OR:_or, NOT:_not, NOP:nop
}

def run(program, stdout=None):
    if stdout == None: stdout = sys.stdout
    global prints
    prints = list()
    regs = [0, 0, 0, 0, 0]
    stack = list()
    pc = 0
    inst = program[pc]
    while True:
        if DEBUG:
            print 'pc =', pc
            print 'inst =', inst
            print 'regs =', regs
            print 'stack =', stack
        #if DEBUG == True or pc > 100:
            #import pdb
            #pdb.set_trace()
        op = inst[0]
        if op == EXIT: break
        if op in A:
            reg = inst[1]
            addr = None
        elif op in B:
            reg = inst[1]
            addr = inst[2]
        else:
            reg = inst[2]
            addr = inst[1]
        pc = INSTS[op](regs, stack, pc, reg, addr)
        inst = program[pc]
        #print
    for p in prints:
        print '>>>>>>', p
        print >>stdout, p


if __name__ == '__main__':
    run([
#init prog
        (IMM, 4, 0), # 0
        (IMM, 3, 0), # 1
        (SAVE, 3, 4), # 2
        (IMM, 3, 1), # 3
        (SAVE, 3, 4), # 4
        (IMM, 3, 2), # 5
        (SAVE, 3, 4), # 6
        (IMM, 1, 3), # 7
# start prog
        (IMM , 4, 0), # 8
        (ADD , 4, 1), # 9
        (IMM , 3, 29), # 10
        (SAVE, 4, 3, 'save arg 1'), # 11
        (IMM , 3, 1), # 12
        (ADD , 4, 3), # 13
        (IMM , 3, 37), # 14
        (SAVE, 4, 3, 'save arg 2'), # 15
        (ADD , 4, 4), # 16

#call func
        (IMM, 3, 33), # 17
        (PC , 2, 0), # 18
        (J  , 3, 0), # 19
#return func

        (IMM, 3, 0), # 20
        (ADD, 3, 1), # 21
        (IMM, 4, 2), # 22
        (SUB, 3, 4), # 23
        (LOAD, 3, 3), # 24
        (PRNT, 3, 3), # 25

        (IMM, 3, 0), # 26
        (ADD, 3, 1), # 27
        (IMM, 4, 1), # 28
        (SUB, 3, 4), # 29
        (LOAD, 3, 3), # 30
        (PRNT, 3, 3), # 31
    #exit
        (EXIT, 0, 0), # 32

#func add
    #stack save
        (IMM, 4, 0, 'START FUNC'), # 33
        (ADD, 4, 1),
        (IMM, 3, 2),
        (ADD, 4, 3, 'reg[4] += 2'),
        (SAVE, 4, 0, 'stack save: save bp'),
        (IMM, 3, 1),
        (ADD, 4, 3, 'reg[4] += 1'),
        (SAVE, 4, 1, 'stack save: save fp'),
        (ADD, 4, 3, 'reg[4] += 1'),
        (SAVE, 4, 2, 'stack save: save ra'),
        (ADD, 4, 3, 'reg[4] += 1'),
        (IMM, 0, 0),
        (ADD, 0, 1, 'mv fp to bp'),
        (IMM, 1, 0),
        (ADD, 1, 4, 'mv $4 to fp'),
    # start func body
        (IMM, 3, 0), # load args
        (ADD, 3, 0),
        (IMM, 4, 1),
        (ADD, 4, 0),
        (LOAD, 3, 3),
        (LOAD, 4, 4),
        (ADD, 4, 3), # do addition

        (SAVE, 1, 4), # save result
        (IMM, 3, 1),
        (ADD, 1, 3, 'reg[1] += 1'),

        (IMM, 3, 15),
        (ADD, 4, 3),

        (SAVE, 1, 4), # save result
        (IMM, 3, 1),
        (ADD, 1, 3, 'reg[1] += 1'),
    # end func body
    #stack restore
        (IMM, 4, 0),
        (ADD, 4, 0, 'load bp into 4'),
        (IMM, 3, 2),
        (ADD, 4, 3, 'reg[4] += 2'),
        (LOAD, 0, 4, 'stack restore: bp'),
        (IMM, 3, 2),
        (ADD, 4, 3, 'reg[4] += 2'),
        (LOAD, 2, 4, 'stack restore: ra'),
        (IMM, 3, 1),
        (SUB, 4, 3, 'reg[4] += 1'),
        (IMM, 3, 0),
        (ADD, 3, 1),
        (LOAD, 1, 4, 'stack restore: fp'),
        (IMM, 4, 2),
        (SUB, 3, 4),
        (LOAD, 4, 3, 'function return loaded'),
        (SAVE, 1, 4, 'save result'), # save result
        (IMM, 4, 1),
        (ADD, 1, 4, 'inc fp'),

        (IMM, 4, 1),
        (ADD, 3, 4),
        (LOAD, 4, 3, 'function return loaded'),
        (SAVE, 1, 4, 'save result'), # save result
        (IMM, 4, 1),
        (ADD, 1, 4, 'inc fp'),

    # return
        (IMM, 4, 0),
        (ADD, 4, 2),
        (J,   4, 0),
#end func
    ])
