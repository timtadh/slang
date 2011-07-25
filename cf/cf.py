#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

## This file is based off of the work and writings of Steven S. Muchnick
## Muchnick, S. "Advanced Compiler Design & Implementation" Academic Press. 1997. Pg. 202-215

import sys

import struct as cfs

class analyze(object):
    '''Produce a structural control flow tree for each function. Takes the output of il_gen as
    input.'''

    @classmethod
    def __mock__(cls):
        self = super(analyze, cls).__new__(cls)
        self.__init__()
        return self

    def __new__(cls, entry, blocks, functions, stdout=None):
        self = super(analyze, cls).__new__(cls)
        self.__init__()
        if stdout is None: self.stdout = sys.stdout
        self.functions = functions

        ## the control flow analysis modifies the graph as we go.
        ## this is undesirable. we would like the underlying graph
        ## to remain. Therefore, we "push" a copy of the current
        ## graph down and pop it back at the end.
        for blk in blocks.itervalues():
            blk.push_links()

        for f in self.functions.itervalues():
            f.tree = self.structure(f)

        for blk in blocks.itervalues():
            blk.pop_links()

        return None

    def __init__(self):
        pass

    ## A post-order Depth First Search traversal.
    def postorder(self, f):
        '''Produces a post order depth-first-search traversal of the graph of the function f.'''
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
        '''Produces a control tree of the function f using structural analysis.'''
        blks = self.postorder(f)

        #postmax = len(blks)-1
        postctr = 0
        while len(blks) > 1 and postctr <= len(blks):
            cblk = blks[postctr]

            ok, rtype, nset = self.acyclic(blks, cblk)
            if ok:
                ## Then we have an acyclic region. reduce the graph.
                newnode, blks, postctr = self.reduce(blks, rtype, nset, postctr)
                #if f.entry in nset:
                    #f.entry = newnode
            elif False:
                pass
                ## if nessesary insert cyclic region detection here
                ## right now, I only have if-statements and functions
                ## so there are no inter-block cycles.
            else:
                postctr += 1

        if len(blks) != 1:
            raise Exception, 'Construction of control tree failed'

        return blks[0]

    def reduce(self, blks, rtype, nset, postctr):
        '''Reduces the graph (blks) by replacing the set (nset) with an abstract node of rtype.
        Also updates postctr appropriately.'''

        def compact(blks, node, nset):
            ## TODO: Refactor this method to use one loop
            max_pos = 0
            for i, b in enumerate(blks):
                if b in nset: max_pos = i

            blks[max_pos] = node
            blks = [b for b in blks if b not in nset]
            return blks

        def replace(blks, node, nset, postctr):
            ## TODO: refactor this method to have compact set postctr
            blks = compact(blks, node, nset)
            for i, b in enumerate(blks):
                if b is node: postctr = i

            for n in nset:
                for v in n.next:
                    if v not in nset:
                        if v not in node.next: node.next.append(v)
                        v.prev.remove(n)
                        if node not in v.prev: v.prev.append(node)
                for u in n.prev:
                    if u not in nset:
                        if u not in node.prev: node.prev.append(u)
                        u.next.remove(n)
                        if node not in u.next: u.next.append(node)
            print blks, postctr
            return blks, postctr

        node = cfs.Node(rtype, nset)
        blks, postctr = replace(blks, node, nset, postctr)
        return node, blks, postctr

    ## Adapted from figure 7.41 on page 208
    def acyclic(self, blks, cblk):
        ''' Detects acyclic control flow regions suchs as: chains and if-statements.'''
        nset = set()

        ## BEGIN CHAIN CHECK:
        ##   Check for a chain of blks starting with the current blk
        n = cblk
        p = True                # len(n.prev) == 1 [assume for start of loop]
        s = (len(n.next) == 1)  # len(n.next) == 1 eg. |successor| == 1

        ## look for a chain starting with the current block
        while p and s:
            nset.add(n)
            n = n.next[0]
            p = (len(n.prev) == 1)
            s = (len(n.next) == 1)

        ## the current blk is part of the chain as well.
        if p:
            nset.add(n)

        ## now look backwards
        n = cblk
        p = (len(n.prev) == 1)
        s = True
        while p and s:
            nset.add(n)
            n = n.prev[0]
            p = (len(n.prev) == 1)
            s = (len(n.next) == 1)

        ## the current blk is part of the chain as well.
        if s:
            nset.add(n)

        ## END CHAIN CHECK
        if len(nset) > 1:  # chain
            return True, cfs.CHAIN, nset
        elif len(cblk.next) == 2: # if-then, if-then-else, ...
            r = cblk.next[0]
            q = cblk.next[1]

            if r.next == q.next and len(r.next[0].prev) == 2: # this is an IF-THEN-ELSE
                return True, cfs.IF_THEN_ELSE, [cblk, r, q]
            elif r.next[0] == q: # this is an IF-THEN
                return True, cfs.IF_THEN, [cblk, r]

        return False, None, None

