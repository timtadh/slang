#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import abstract
import il

class ReachingDefintions(abstract.DataFlowAnalyzer):

    def __init__(self):
        self.def_count = 0

    def init(self, blocks, functions):
        defs = list()
        for name, blk in blocks.iteritems():
            for i, inst in enumerate(blk.insts):
                #if isinstance(i.a, il.Symbol): vars.add(i.a.id)
                #if isinstance(i.b, il.Symbol): vars.add(i.b.id)
                if isinstance(inst.result, il.Symbol): defs.append(inst.result.id)
        self.def_count = len(defs)
        print defs
        print self.def_count

    def flow_function(self, blk): pass

    def newelement(self): pass
    def meet(self, a, b): pass
    def join(self, a, b): pass
    def compose(self, a, b): pass
    def star(self, a, b): pass
