#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import abc

class DataFlowAnalyzer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def init(self, blocks, functions):
        '''collect and initialize the analyzer.'''

    @abc.abstractmethod
    def flow_function(self, blk):
        '''Produce a flow function for the given blk.

        @blk = can be either a il.Block or a cf.struct.Node
        '''

    @abc.abstractmethod
    def newelement(self):
        '''create a new lattice element.'''

    @abc.abstractmethod
    def meet(self, a, b):
        '''the meet operator on the underlying lattice'''

    @abc.abstractmethod
    def join(self, a, b):
        '''the join operator on the underlying lattice'''

    @abc.abstractmethod
    def compose(self, a, b):
        '''compose flow functions together, eg. a(b(x))'''

    @abc.abstractmethod
    def star(self, a, b):
        '''the kleene star on the induced lattice of the flow functions'''
