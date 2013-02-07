
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

import abstract, il
from lib import DFS

## The taint flow function:
##              +-
##              | x U {v}     if v := a op b and tainted(a) or tainted(b)
##  f(s, x) = --+
##              | x           otherwise
##              +-

def istainted(func):
    if 'taint' in func.name: return True
    return False

class TaintFlow(abstract.DataFlowAnalyzer):

    name = 'taintflow'
    direction = 'forward'

    def __init__(self, f, debug=False):
        self.debug = debug
        for blk in f.blks:
            iprms = list()
            call = None
            for i, inst in enumerate(blk.insts):
                if inst.op == il.IPRM:
                    iprms.append(inst)
                elif inst.op == il.CALL:
                    setattr(inst, 'iprms', iprms)
                    setattr(inst, 'rprms', list())
                    call = inst
                elif inst.op == il.RPRM:
                    call.rprms.append(inst)

    def flow_function(self, blk):
        #prev_blks = DFS(blk, 'prev')
        def instflow(inst):
            def flow(tainted):
                def istaint(i)
                    if isinstance(i.a, il.Symbol) and i.a.type.id in tainted:
                        return True
                    elif isinstance(i.b, il.Symbol) and i.b.type.id in tainted:
                        return True
                    else:
                        return False
                if isinstance(inst.result, il.Symbol) and inst.op != il.RPRM:
                    if istaint(inst):
                        return tainted | set([inst.result.type.id])
                elif inst.op == il.CALL:
                    func = inst.a.type
                    if ((isinstance(func, il.Func) and istainted(func)) or
                      any(istaint(iprm) for iprm in inst.iprms)):
                        new = set()
                        for rprm in inst.rprms:
                            new.add(rprm.result.type.id)
                        return tainted | new
                return tainted
            return x

        flowfuncs = list()
        for i, inst in enumerate(blk.insts):
            flowfuncs.append(instflow(inst))
        #print
        #print 'include', include
        #print 'included_types', included_types
        #print 'exclude', exclude
        #print
        #print prev_blks
        #print

        def flowfunc(flowfuncs, tainted):
            acc = tainted
            for f in flowfuncs:
                acc = f(acc)
            return acc

        return functools.partial(flowfunc, flowfuncs)

    def newelement(self): return set()
    def id(self, a): return set(a)
    def meet(self, a, b): return a & b
    def join(self, a, b): return a | b

    def star(self, f):
        def h(x):
            return self.join(self.id(x), f(x))
        return h

