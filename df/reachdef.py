#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

import abstract, il
from lib import DFS


class ReachingDefinitions(abstract.DataFlowAnalyzer):

    name = 'reachdef'
    direction = 'forward'

    def __init__(self, f, debug=False):
        self.debug = debug
        self.types = dict()
        for blk in f.blks:
            for i, inst in enumerate(blk.insts):
                if isinstance(inst.result, il.Symbol):
                    if inst.result.type.id not in self.types:
                        self.types[inst.result.type.id] = set()
                    self.types[inst.result.type.id].add((blk.name, i))

    def flow_function(self, blk):
        include = set()
        included_types = set()
        exclude = set()
        #prev_blks = DFS(blk, 'prev')
        for i, inst in enumerate(blk.insts[-1::-1]):
            i = len(blk.insts) - (i + 1)
            if isinstance(inst.result, il.Symbol):
                if inst.result.type.id in included_types: continue
                typ = inst.result.type.id
                loc = (blk.name, i)
                #print (blk.name, i), typ
                include.add(loc)
                included_types.add(typ)
                #exclude |= set((b,i) for b, i in self.types[typ] if b in prev_blks) - set([loc])
                exclude |= self.types[typ] - set([loc])
        #print
        #print 'include', include
        #print 'included_types', included_types
        #print 'exclude', exclude
        #print
        #print prev_blks
        #print

        def flowfunc(include, exclude, flow):
            result = (flow | include) - exclude
            return result

        return functools.partial(flowfunc, include, exclude)

    def newelement(self): return set()
    def id(self, a): return set(a)
    def meet(self, a, b): return a & b
    def join(self, a, b): return a | b

    def star(self, f):
        def h(x):
            return self.join(self.id(x), f(x))
        return h
