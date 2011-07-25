#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import abstract

class ReachingDefintions(abstract.DataFlowAnalyzer):

    def init(self, blocks, functions):
        for b in blocks:
            print b

    def flow_function(self, blk): pass
    def newelement(self): pass
    def meet(self, a, b): pass
    def join(self, a, b): pass
    def compose(self, a, b): pass
    def star(self, a, b): pass
