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

    def init(self, f):
        print f
        defs = list()
        for blk in f.blks:
            name = blk.name
            for i, inst in enumerate(blk.insts):
                if isinstance(inst.result, il.Symbol):
                    print (name, blk), inst.result.id
                    defs.append(inst.result.id)
        self.def_count = len(defs)
        print defs
        print self.def_count

    def flow_function(self, blk): pass

    def newelement(self): pass
    def meet(self, a, b): pass
    def join(self, a, b): pass
    def compose(self, a, b): pass
    def star(self, a, b): pass
