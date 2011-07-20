#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys

typesr = (
    'CHAIN', 'IF_THEN', 'IF_THEN_ELSE',
)
types = dict((k, i) for i, k in enumerate(typesr))
sys.modules[__name__].__dict__.update(types)

class Node(object):

    def __init__(self, rtype, blks):
        self.region_type = rtype
        self.blks = list(blks)
        self.next = list()
        self.prev = list()

    @property
    def name(self):
        return '(' + ' '.join([b.name for b in self.blks]) + ')'

    def __repr__(self): return str(self)

    def __str__(self):
        return (
            '<cf.Node %s (%s)>'
        ) % (typesr[self.region_type], ' '.join([b.name for b in self.blks]))
