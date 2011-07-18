#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

## This file is based off of the work and writings of Steven S. Muchnick
## Muchnick, S. "Advanced Compiler Design & Implementation" Academic Press. 1997. Pg. 202-215

import sys

class analyze(object):

    def __new__(cls, entry, blocks, functions, stdout=None):
        self = super(analyze, cls).__new__(cls)
        self.__init__()
        if stdout is None: self.stdout = sys.stdout
        self.functions = functions


        for f in self.functions.itervalues():
            print f.name
            self.structure(f)
            print
        print

        return None

    def __init__(self):
        pass

    ## A post-order Depth First Search traversal.
    def postorder(self, f):

        visited = set()
        order = list()

        def visit(blk):
            visited.add(blk.name)
            for b in blk.next:
                if b.name not in visited:
                    visit(b)
            order.append(blk)

        visit(f.entry)
        return order

    def structure(self, f):
        blks = self.postorder(f)

        postmax = len(blks)-1
        postctr = 1
        while len(blks) > 1 and postctr <= postmax:
            n = blks[postctr]
            print n

            break

    def acyclic(self, f, blks, cblk, postmax, postctr):
        nset = set()

        ## Check for a chain of blks starting with the current blk

