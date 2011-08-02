#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

import abstract
import il

class ReachingDefintions(abstract.DataFlowAnalyzer):

    def __init__(self):
        self.defs = dict()
        self.types = dict()

    def init(self, f):
        defs = list()
        for blk in f.blks:
            for i, inst in enumerate(blk.insts):
                if isinstance(inst.result, il.Symbol):
                    self.defs[(blk.name, i)] = inst.result.type
                    if inst.result.type.id not in self.types:
                        self.types[inst.result.type.id] = set()
                    self.types[inst.result.type.id].add((blk.name, i))
        print self.defs
        print self.types
        print self.types.keys()

    def flow_function(self, blk):
        include = set()
        included_types = set()
        exclude = set()
        for i, inst in enumerate(blk.insts[-1::-1]):
            i = len(blk.insts) - (i + 1)
            if isinstance(inst.result, il.Symbol):
                if inst.result.type.id in included_types: continue
                typ = inst.result.type.id
                loc = (blk.name, i)
                #print (blk.name, i), typ
                include.add(loc)
                included_types.add(typ)
                exclude |= self.types[typ] - set([loc])
        print
        print include
        print included_types
        print exclude

        def flowfunc(include, exclude, flow):
            return (flow | include) - exclude

        return functools.partial(flowfunc, include, exclude)

    def newelement(self): pass
    def meet(self, a, b): pass
    def join(self, a, b): pass
    def compose(self, a, b): pass
    def star(self, a, b): pass
