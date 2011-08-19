#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import functools

import abstract, il
from lib import DFS

class LiveVariable(abstract.DataFlowAnalyzer):

    name = 'livevar'
    direction = 'backward'

    def __init__(self, f): pass

    def flow_function(self, blk):
        defb = set()
        useb = set()

        for inst in blk.insts:
            if isinstance(inst.a, il.Symbol):
                if inst.a.type.id not in defb: useb.add(inst.a.type.id)
            if isinstance(inst.b, il.Symbol):
                if inst.b.type.id not in defb: useb.add(inst.b.type.id)
            if isinstance(inst.result, il.Symbol):
                if inst.result.type.id not in useb: defb.add(inst.result.type.id)

        def flowfunc(useb, defb, flow):
            print 'flow function for', blk.name
            print ' '*4, 'use', useb
            print ' '*4, 'def', defb
            result = useb | (flow - defb)
            return result

        return functools.partial(flowfunc, useb, defb)

    def newelement(self): return set()
    def id(self, a): return set(a)
    def meet(self, a, b): return a & b
    def join(self, a, b): return a | b

    def star(self, f):
        def h(x):
            return self.meet(self.id(x), f(x))
