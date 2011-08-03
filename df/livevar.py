#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

import abstract, il
from lib import DFS


class ReachingDefintions(abstract.DataFlowAnalyzer):

    name = 'ReachingDefinitionsExample'
    direction = 'forward'

    def __init__(self, f):
        self.defs = dict()
        self.types = dict()
        defs = list()
        for blk in f.blks:
            for i, inst in enumerate(blk.insts):
                if isinstance(inst.result, il.Symbol):
                    self.defs[(blk.name, i)] = inst.result.type
                    if inst.result.type.id not in self.types:
                        self.types[inst.result.type.id] = set()
                    self.types[inst.result.type.id].add((blk.name, i))
        #print self.defs
        #print self.types
        #print self.types.keys()

    def flow_function(self, blk):
        raise Exception

    def newelement(self): return set()
    def id(self, a): return set(a)
    def meet(self, a, b): return a & b
    def join(self, a, b): return a | b

    def star(self, f):
        def h(x):
            return self.meet(self.id(x), f(x))
