#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import abc

class DataFlowAnalyzer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def direction(self):
        '''the direction of the analyzer either 'forward' or 'backward' '''

    @abc.abstractproperty
    def name(self):
        '''the name of this analyzer'''

    @abc.abstractmethod
    def __init__(self, f, debug):
        '''collect and initialize the analyzer.'''

    @abc.abstractmethod
    def flow_function(self, blk):
        '''Produce a flow function for the given blk.

        @blk = can be either a il.Block or a cf.struct.Node
        '''

    @abc.abstractmethod
    def id(self, a):
        '''the identity flow function'''

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
    def star(self, a, b):
        '''the kleene star on the induced lattice of the flow functions'''

    @staticmethod
    def has_result_method():
        '''Has a custom result function been defined to attach to "function"
        objs?'''
        return False

    def get_result_method(self):
        '''Get the custom result function to attach to the function object.'''
        return None

